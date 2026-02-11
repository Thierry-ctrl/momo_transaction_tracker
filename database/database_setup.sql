-- database/database_setup.sql
-- MoMo Transaction Tracker — SQLite Database Setup
-- Unlike the original project which used MySQL, we use SQLite here
-- so you don't need to install a separate database server.

-- ============================================================
-- Drop existing tables (reset everything)
-- ============================================================

DROP TABLE IF EXISTS transaction_labels;
DROP TABLE IF EXISTS audit_trail;
DROP TABLE IF EXISTS transactions;
DROP TABLE IF EXISTS labels;
DROP TABLE IF EXISTS categories;
DROP TABLE IF EXISTS users;

-- ============================================================
-- Users — senders and receivers of MoMo transactions
-- ============================================================

CREATE TABLE users (
  user_id      INTEGER PRIMARY KEY AUTOINCREMENT,
  phone_number TEXT    NOT NULL UNIQUE,  -- Rwandan format: 250788xxxxxx
  full_name    TEXT    NOT NULL,
  created_at   TEXT    NOT NULL DEFAULT (datetime('now'))
);

-- ============================================================
-- Categories — types of mobile money transactions
-- ============================================================

CREATE TABLE categories (
  category_id  INTEGER PRIMARY KEY AUTOINCREMENT,
  name         TEXT    NOT NULL UNIQUE,
  created_at   TEXT    NOT NULL DEFAULT (datetime('now'))
);

-- ============================================================
-- Transactions — core table storing every MoMo transaction
-- ============================================================

CREATE TABLE transactions (
  transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
  tx_ref         TEXT    NOT NULL UNIQUE,  -- MoMo reference like TXN20260201001
  sender_id      INTEGER NOT NULL,
  receiver_id    INTEGER NOT NULL,
  category_id    INTEGER NOT NULL,
  amount         REAL    NOT NULL CHECK (amount >= 0),
  fee            REAL    NOT NULL DEFAULT 0 CHECK (fee >= 0),
  balance_after  REAL    NULL,
  timestamp      TEXT    NOT NULL,
  description    TEXT    NULL,
  created_at     TEXT    NOT NULL DEFAULT (datetime('now')),

  FOREIGN KEY (sender_id)   REFERENCES users(user_id)      ON DELETE RESTRICT ON UPDATE CASCADE,
  FOREIGN KEY (receiver_id) REFERENCES users(user_id)      ON DELETE RESTRICT ON UPDATE CASCADE,
  FOREIGN KEY (category_id) REFERENCES categories(category_id) ON DELETE RESTRICT ON UPDATE CASCADE
);

-- Performance indexes
CREATE INDEX idx_tx_timestamp  ON transactions(timestamp);
CREATE INDEX idx_tx_sender     ON transactions(sender_id);
CREATE INDEX idx_tx_receiver   ON transactions(receiver_id);
CREATE INDEX idx_tx_ref        ON transactions(tx_ref);
CREATE INDEX idx_tx_cat_time   ON transactions(category_id, timestamp);

-- ============================================================
-- Labels — tags you can assign to transactions
-- ============================================================

CREATE TABLE labels (
  label_id    INTEGER PRIMARY KEY AUTOINCREMENT,
  label_name  TEXT    NOT NULL UNIQUE,
  created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
);

-- ============================================================
-- Transaction Labels — junction table (many-to-many)
-- ============================================================

CREATE TABLE transaction_labels (
  transaction_id INTEGER NOT NULL,
  label_id       INTEGER NOT NULL,
  assigned_at    TEXT    NOT NULL DEFAULT (datetime('now')),

  PRIMARY KEY (transaction_id, label_id),

  FOREIGN KEY (transaction_id) REFERENCES transactions(transaction_id) ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (label_id)       REFERENCES labels(label_id)             ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE INDEX idx_txl_label ON transaction_labels(label_id);

-- ============================================================
-- Audit Trail — tracks API operations (different from original's system_logs)
-- This table logs WHO did WHAT and from WHERE, which is more useful
-- for security auditing than simple system logs.
-- ============================================================

CREATE TABLE audit_trail (
  audit_id       INTEGER PRIMARY KEY AUTOINCREMENT,
  action         TEXT    NOT NULL,  -- 'CREATE', 'UPDATE', 'DELETE', 'READ'
  entity_type    TEXT    NOT NULL,  -- 'transaction', 'user', etc.
  entity_id      INTEGER NULL,
  performed_by   TEXT    NULL,      -- token identifier or username
  ip_address     TEXT    NULL,      -- client IP address
  details        TEXT    NULL,      -- JSON string with extra context
  created_at     TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX idx_audit_action  ON audit_trail(action);
CREATE INDEX idx_audit_entity  ON audit_trail(entity_type, entity_id);
CREATE INDEX idx_audit_time    ON audit_trail(created_at);


-- ============================================================
-- SAMPLE DATA — Rwandan users, categories, transactions
-- ============================================================

-- Users (Rwandan phone numbers starting with 250)
INSERT INTO users (phone_number, full_name) VALUES
('250788100001', 'Jean Pierre Habimana'),
('250788200002', 'Marie Claire Uwase'),
('250788300003', 'MTN Rwanda'),
('250788400004', 'Patrick Mugabo'),
('250788500005', 'WASAC Ltd'),
('250788600006', 'Aline Mukamana'),
('250788700007', 'Emmanuel Niyonzima'),
('250788800008', 'Savings Account'),
('250788900009', 'Agent Kigali 042');

-- Transaction categories (7 types — one more than the original)
INSERT INTO categories (name) VALUES
('P2P Transfer'),
('Airtime Purchase'),
('Utility Bill Payment'),
('Merchant Payment'),
('International Remittance'),
('Cash Withdrawal'),
('Savings Deposit');  -- This is the extra category we added

-- Labels
INSERT INTO labels (label_name) VALUES
('Normal'),
('High Value'),
('Potential Fraud'),
('Recurring'),
('Family Support'),
('Business'),
('Government Service');

-- Sample transactions
INSERT INTO transactions (tx_ref, sender_id, receiver_id, category_id, amount, fee, balance_after, timestamp, description) VALUES
('TXN20260201001', 1, 2, 1, 15000.00, 150.00, 45000.00,  '2026-02-01 08:30:15', 'Sent money to friend'),
('TXN20260201002', 1, 3, 2, 500.00,   0.00,   44500.00,  '2026-02-01 09:12:44', 'Airtime top-up'),
('TXN20260201003', 4, 1, 1, 32000.00, 320.00, 76500.00,  '2026-02-01 10:45:20', 'Rent payment from Patrick'),
('TXN20260202001', 1, 5, 3, 8500.50,  100.00, 67899.50,  '2026-02-02 07:20:33', 'Water bill payment'),
('TXN20260202002', 6, 3, 4, 2500.00,  50.00,  12300.00,  '2026-02-02 11:05:10', 'Birth certificate application'),
('TXN20260203001', 1, 8, 7, 20000.00, 0.00,   47899.50,  '2026-02-03 14:00:00', 'Monthly savings'),
('TXN20260203002', 4, 9, 6, 50000.00, 750.00, 25000.00,  '2026-02-03 16:22:18', 'Cash out at agent'),
('TXN20260204001', 6, 2, 1, 7500.00,  100.00, 4700.00,   '2026-02-04 09:30:55', 'School fees contribution'),
('TXN20260204002', 7, 1, 5, 120000.00,1200.00,350000.00, '2026-02-04 13:15:42', 'Diaspora family support'),
('TXN20260205001', 2, 3, 2, 1000.00,  0.00,   22300.00,  '2026-02-05 08:00:05', 'Weekly airtime bundle');

-- Assign labels to transactions
INSERT INTO transaction_labels (transaction_id, label_id) VALUES
(1, 1),           -- Normal
(3, 1), (3, 2),   -- Normal + High Value
(5, 7),           -- Government Service
(6, 4),           -- Recurring
(7, 2), (7, 6),   -- High Value + Business
(8, 5),           -- Family Support
(9, 2), (9, 5),   -- High Value + Family Support
(10, 4);          -- Recurring

-- Audit trail sample entries
INSERT INTO audit_trail (action, entity_type, entity_id, performed_by, ip_address, details) VALUES
('CREATE', 'transaction', 1, 'csv_parser', '127.0.0.1', '{"source": "momo_messages.csv", "row": 1}'),
('CREATE', 'transaction', 2, 'csv_parser', '127.0.0.1', '{"source": "momo_messages.csv", "row": 2}'),
('READ',   'transaction', NULL, 'api_user', '192.168.1.10', '{"endpoint": "/transactions", "method": "GET"}'),
('UPDATE', 'transaction', 3, 'api_user', '192.168.1.10', '{"field": "description", "old": "Rent", "new": "Rent payment from Patrick"}'),
('DELETE', 'transaction', NULL, 'api_user', '10.0.0.5', '{"attempted_id": 999, "result": "not_found"}');
