#!/bin/sh

# Dash version based on: https://github.com/twitter/mysql/commit/4c366d191061094c9d95a705dd58a6beed2c5987

# Copyright (c) 2002, 2012, Oracle and/or its affiliates. All rights reserved.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301  USA

config=".my.cnf.$$"
command=".mysql.$$"
mysql_client=""

trap "interrupt" 1 2 3 6 15

rootpass=""
echo_n=
echo_c=

set_echo_compat() {
    case `echo "testing\c"`,`echo -n testing` in
	*c*,-n*) echo_n=   echo_c=     ;;
	*c*,*)   echo_n=-n echo_c=     ;;
	*)       echo_n=   echo_c='\c' ;;
    esac
}

prepare() {
    touch $config $command
    chmod 600 $config $command
}

find_mysql_client()
{
  for n in ./bin/mysql mysql
  do
    $n --no-defaults --help > /dev/null 2>&1
    status=$?
    if test $status -eq 0
    then
      mysql_client=$n
      return
    fi
  done
  echo "Can't find a 'mysql' client in PATH or ./bin"
  exit 1
}

do_query() {
    echo "$1" >$command
    #sed 's,^,> ,' < $command  # Debugging
    $mysql_client --defaults-file=$config <$command
    return $?
}

# Simple escape mechanism (\-escape any ' and \), suitable for two contexts:
# - single-quoted SQL strings
# - single-quoted option values on the right hand side of = in my.cnf
#
# These two contexts don't handle escapes identically.  SQL strings allow
# quoting any character (\C => C, for any C), but my.cnf parsing allows
# quoting only \, ' or ".  For example, password='a\b' quotes a 3-character
# string in my.cnf, but a 2-character string in SQL.
#
# This simple escape works correctly in both places.
basic_single_escape () {
    # The quoting on this sed command is a bit complex.  Single-quoted strings
    # don't allow *any* escape mechanism, so they cannot contain a single
    # quote.  The string sed gets (as argv[1]) is:  s/\(['\]\)/\\\1/g
    #
    # Inside a character class, \ and ' are not special, so the ['\] character
    # class is balanced and contains two characters.
    echo "$1" | sed 's/\(['"'"'\]\)/\\\1/g'
}

make_config() {
    echo "# mysql_secure_installation config file" >$config
    echo "[mysql]" >>$config
    echo "user=root" >>$config
    esc_pass=`basic_single_escape "$rootpass"`
    echo "password='$esc_pass'" >>$config
    #sed 's,^,> ,' < $config  # Debugging
}

get_root_password() {
    status=1
    while [ $status -eq 1 ]; do
	stty -echo
	echo $echo_n "Enter current password for root (enter for none): $echo_c"
	read password
	echo
	stty echo
	if [ "x$password" = "x" ]; then
	    hadpass=0
	else
	    hadpass=1
	fi
	rootpass=$password
	make_config
	do_query ""
	status=$?
    done
    echo "OK, successfully used password, moving on..."
    echo
}

set_root_password() {
    stty -echo
    echo $echo_n "New password: $echo_c"
    read password1
    echo
    echo $echo_n "Re-enter new password: $echo_c"
    read password2
    echo
    stty echo

    if [ "$password1" != "$password2" ]; then
	echo "Sorry, passwords do not match."
	echo
	return 1
    fi

    if [ "$password1" = "" ]; then
	echo "Sorry, you can't use an empty password here."
	echo
	return 1
    fi

    esc_pass=`basic_single_escape "$password1"`
    do_query "UPDATE mysql.user SET Password=PASSWORD('$esc_pass') WHERE User='root';"
    if [ $? -eq 0 ]; then
	echo "Password updated successfully!"
	echo "Reloading privilege tables.."
	reload_privilege_tables
	if [ $? -eq 1 ]; then
		clean_and_exit
	fi
	echo
	rootpass=$password1
	make_config
    else
	echo "Password update failed!"
	clean_and_exit
    fi

    return 0
}

remove_anonymous_users() {
    do_query "DELETE FROM mysql.user WHERE User='';"
    if [ $? -eq 0 ]; then
	echo " ... Success!"
    else
	echo " ... Failed!"
	clean_and_exit
    fi

    return 0
}

remove_remote_root() {
    do_query "DELETE FROM mysql.user WHERE User='root' AND Host NOT IN ('localhost', '127.0.0.1', '::1');"
    if [ $? -eq 0 ]; then
	echo " ... Success!"
    else
	echo " ... Failed!"
    fi
}

remove_test_database() {
    echo " - Dropping test database..."
    do_query "DROP DATABASE IF EXISTS test;"
    if [ $? -eq 0 ]; then
	echo " ... Success!"
    else
	echo " ... Failed!  Not critical, keep moving..."
    fi

    echo " - Removing privileges on test database..."
    do_query "DELETE FROM mysql.db WHERE Db='test' OR Db='test\\_%'"
    if [ $? -eq 0 ]; then
	echo " ... Success!"
    else
	echo " ... Failed!  Not critical, keep moving..."
    fi

    return 0
}

reload_privilege_tables() {
    do_query "FLUSH PRIVILEGES;"
    if [ $? -eq 0 ]; then
	echo " ... Success!"
	return 0
    else
	echo " ... Failed!"
	return 1
    fi
}

interrupt() {
    echo
    echo "Aborting!"
    echo
    cleanup
    stty echo
    exit 1
}

cleanup() {
    echo "Cleaning up..."
    rm -f $config $command
}

# Remove the files before exiting.
clean_and_exit() {
	cleanup
	exit 1
}

#----------------------------------------------------------------
# Dash Automation
#----------------------------------------------------------------
create_db() {
    create_schema=$(cat "database/create-db.sql")
    do_query "$create_schema"
    echo "..done"
}

init_db() {
    init_schema=$(cat "database/sentinel.mysql")
    do_query "USE sentinel; $init_schema"
    do_query "USE sentinel_test; $init_schema"
    echo "..done"
}

echo "\n======================================================"
echo "*                                                    *"
echo "*     DASH SENTINEL - MYSQL DATABASE SETUP           *"
echo "*                                                    *"
echo "*  -Configure MySQL for Sentinel Masternode usage    *"
echo "*  -Create Sentinel Databases and Users              *"
echo "*  -Any existing Sentinel data will be deleted       *"
echo "*                                                    *"
echo "======================================================\n"

prepare
find_mysql_client
set_echo_compat
get_root_password

echo "\nRemoving anonymous user access"
remove_anonymous_users

echo "\nRemoving remote root access"
remove_remote_root

echo "\nRemoving test database"
remove_test_database

echo "\nReloading Privileges"
reload_privilege_tables

echo "\nCreating Database and Users"
create_db

echo "\nCreating Database Objects"
init_db

cleanup

echo "\nEnsure MySQL launches after reboot"
sudo /usr/sbin/update-rc.d mysql defaults
echo "..done"

# TODO: edit /etc/mysql/my.cnf using sed
#echo "\nSet Global Config"
    # block connections from anywhere except loopback
    #bind-address = 127.0.0.1
    # prevent MySQL access to underlying filesystem
    #local-infile=0

echo "\n====  DASH SENTINEL - MYSQL SETUP COMPLETE ====\n"
#----------------------------------------------------------------
