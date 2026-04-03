CREATE DATABASE IF NOT EXISTS maple_guild_app CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE maple_guild_app;

CREATE TABLE IF NOT EXISTS app_users (
  id INT NOT NULL AUTO_INCREMENT,
  username VARCHAR(50) NOT NULL,
  email VARCHAR(255) NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  full_name VARCHAR(100) NOT NULL,
  provider VARCHAR(50) NOT NULL DEFAULT 'local',
  role ENUM('admin','user') NOT NULL DEFAULT 'user',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  is_active TINYINT(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (id),
  UNIQUE KEY ux_app_users_username (username),
  UNIQUE KEY ux_app_users_email (email),
  KEY ix_app_users_role (role),
  KEY ix_app_users_is_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS app_user_sessions (
  id INT NOT NULL AUTO_INCREMENT,
  user_id INT NOT NULL,
  session_token VARCHAR(255) NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  expires_at DATETIME NOT NULL,
  is_active TINYINT(1) NOT NULL DEFAULT 1,
  ip_address VARCHAR(45),
  user_agent TEXT,
  PRIMARY KEY (id),
  UNIQUE KEY ux_app_user_sessions_session_token (session_token),
  KEY ix_app_user_sessions_user_id (user_id),
  KEY ix_app_user_sessions_expires_at (expires_at),
  KEY ix_app_user_sessions_is_active (is_active),
  CONSTRAINT fk_app_user_sessions_user FOREIGN KEY (user_id) REFERENCES app_users (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

