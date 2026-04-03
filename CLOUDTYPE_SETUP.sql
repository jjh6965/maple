-- =====================================================
-- Cloudtype MariaDB 초기 설정 SQL
-- 실행 위치: Cloudtype MariaDB 웹 대시보드 또는 CLI
-- =====================================================

-- 1. 데이터베이스 생성
CREATE DATABASE IF NOT EXISTS maple_guild_app 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

-- 2. 사용자 생성
CREATE USER IF NOT EXISTS 'maple_app'@'%' IDENTIFIED BY '12dpdjfh!!';

-- 3. 권한 부여
GRANT ALL PRIVILEGES ON maple_guild_app.* TO 'maple_app'@'%' WITH GRANT OPTION;

-- 4. 권한 적용
FLUSH PRIVILEGES;

-- 5. 확인
SELECT USER(), DATABASE(), NOW() as current_time;
