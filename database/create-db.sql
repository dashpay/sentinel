SET @user_pwd = 'sentinel';

# Create/Recreate the Sentinel main and test database
DROP DATABASE IF EXISTS `sentinel`;
DROP DATABASE IF EXISTS `sentinel_test`;
CREATE DATABASE `sentinel` DEFAULT CHARACTER SET utf8 COLLATE utf8_bin ;
CREATE DATABASE `sentinel_test` DEFAULT CHARACTER SET utf8 COLLATE utf8_bin ;

# Create the user
DROP USER IF EXISTS 'sentinel'@'localhost';
SET @create_user = CONCAT("CREATE USER 'sentinel'@'localhost' IDENTIFIED BY '",@user_pwd,"';");
PREPARE stat FROM @create_user;
EXECUTE stat;

# Grant privileges
GRANT SELECT, INSERT, UPDATE, DELETE ON sentinel.* TO 'sentinel'@'localhost';
GRANT SELECT, INSERT, UPDATE, DELETE ON sentinel_test.* TO 'sentinel'@'localhost';
FLUSH PRIVILEGES