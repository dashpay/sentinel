SET @user_pwd = 'dashdrive';

# Create/Recreate the Sentinel main and test database
DROP DATABASE IF EXISTS `sentinel`;
DROP DATABASE IF EXISTS `sentinel_test`;
CREATE DATABASE `sentinel` DEFAULT CHARACTER SET utf8 COLLATE utf8_bin ;
CREATE DATABASE `sentinel_test` DEFAULT CHARACTER SET utf8 COLLATE utf8_bin ;

# Create the user
DROP USER IF EXISTS 'dashdrive'@'localhost';
SET @create_user = CONCAT("CREATE USER 'dashdrive'@'localhost' IDENTIFIED BY '",@user_pwd,"';");
PREPARE stat FROM @create_user;
EXECUTE stat;

# Grant privileges
GRANT SELECT, INSERT, UPDATE, DELETE ON sentinel.* TO 'dashdrive'@'localhost';
GRANT SELECT, INSERT, UPDATE, DELETE ON sentinel_test.* TO 'dashdrive'@'localhost';
FLUSH PRIVILEGES