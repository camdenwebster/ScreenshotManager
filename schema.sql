CREATE TABLE IF NOT EXISTS screenshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL,
    filepath TEXT NOT NULL,
    language TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS IgnoreRegions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    screenshot_id INTEGER,
    description TEXT,
    x INTEGER,
    y INTEGER,
    width INTEGER,
    height INTEGER,
    FOREIGN KEY(screenshot_id) REFERENCES screenshots(id)
);

CREATE TABLE IF NOT EXISTS OperatingSystems (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    version_num INTEGER NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS ScreenshotOperatingSystem (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    screenshot_id INTEGER,
    os_id INTEGER,
    FOREIGN KEY(screenshot_id) REFERENCES screenshots(id),
    FOREIGN KEY(os_id) REFERENCES OperatingSystems(id)
);

CREATE TABLE IF NOT EXISTS AuditLog (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    screenshot_id INTEGER,
    os_id INTEGER,
    ignore_region_id INTEGER,
    date DATETIME NOT NULL,
    FOREIGN KEY(screenshot_id) REFERENCES screenshots(id),
    FOREIGN KEY(os_id) REFERENCES OperatingSystems(id),
    FOREIGN KEY(ignore_region_id) REFERENCES IgnoreRegions(id)
);

-- Trigger to log deletion of screenshots
CREATE TRIGGER IF NOT EXISTS log_screenshot_deletion
AFTER DELETE ON screenshots
FOR EACH ROW
BEGIN
    INSERT INTO AuditLog (screenshot_id, date) VALUES (OLD.id, DATETIME('now'));
END;

-- Trigger to log deletion of operating system versions
CREATE TRIGGER IF NOT EXISTS log_os_deletion
AFTER DELETE ON OperatingSystems
FOR EACH ROW
BEGIN
    INSERT INTO AuditLog (os_id, date) VALUES (OLD.id, DATETIME('now'));
END;

-- Trigger to log deletion of ignore regions
CREATE TRIGGER IF NOT EXISTS log_ignoreregion_deletion
AFTER DELETE ON IgnoreRegions
FOR EACH ROW
BEGIN
    INSERT INTO AuditLog (ignore_region_id, date) VALUES (OLD.id, DATETIME('now'));
END;

-- Indexes
CREATE INDEX IF NOT EXISTS idx_screenshots_filename ON screenshots(filename);
CREATE INDEX IF NOT EXISTS idx_screenshots_filepath ON screenshots(filepath);
CREATE INDEX IF NOT EXISTS idx_ignore_regions_screenshot_id ON IgnoreRegions(screenshot_id);
CREATE INDEX IF NOT EXISTS idx_screenshot_operating_system_screenshot_id ON ScreenshotOperatingSystem(screenshot_id);
CREATE INDEX IF NOT EXISTS idx_screenshot_operating_system_os_id ON ScreenshotOperatingSystem(os_id);
CREATE INDEX IF NOT EXISTS idx_audit_log_screenshot_id ON AuditLog(screenshot_id);
CREATE INDEX IF NOT EXISTS idx_audit_log_os_id ON AuditLog(os_id);

