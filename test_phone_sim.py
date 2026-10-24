import unittest
import os
import csv
from phone_sim import ensure_files, read_users, write_users, append_log, launch_phone, DATABASE_FILE, LOG_FILE


class TestPhoneSim(unittest.TestCase):
    def setUp(self):
        self.db_backup = None
        self.log_backup = None
        if os.path.exists(DATABASE_FILE):
            with open(DATABASE_FILE, 'r', encoding='utf-8') as f:
                self.db_backup = f.read()
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, 'r', encoding='utf-8') as f:
                self.log_backup = f.read()
        if os.path.exists(DATABASE_FILE):
            os.remove(DATABASE_FILE)
        if os.path.exists(LOG_FILE):
            os.remove(LOG_FILE)
    def tearDown(self):
        if os.path.exists(DATABASE_FILE):
            os.remove(DATABASE_FILE)
        if os.path.exists(LOG_FILE):
            os.remove(LOG_FILE)
        if self.db_backup:
            with open(DATABASE_FILE, 'w', encoding='utf-8') as f:
                f.write(self.db_backup)
        if self.log_backup:
            with open(LOG_FILE, 'w', encoding='utf-8') as f:
                f.write(self.log_backup)
    def test_ensure_files(self):
        self.assertFalse(os.path.exists(DATABASE_FILE))
        self.assertFalse(os.path.exists(LOG_FILE))
        ensure_files()
        self.assertTrue(os.path.exists(DATABASE_FILE))
        self.assertTrue(os.path.exists(LOG_FILE))
        with open(DATABASE_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]['user'], 'abdullah')
            self.assertEqual(rows[0]['phone'], '966123456')
            self.assertEqual(rows[0]['balance'], '2450.00')
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = next(reader)
            self.assertEqual(header, ['timestamp', 'user', 'action', 'amount', 'balance_after'])
    



    def test_read_users(self):
        ensure_files()
        users = read_users()
        self.assertIsInstance(users, list)
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0]['user'], 'abdullah')
        self.assertEqual(users[0]['phone'], '966123456')
        self.assertEqual(users[0]['balance'], '2450.00')
    def test_write_users(self):
        ensure_files()
        users = read_users()
        users[0]['balance'] = '3000.00'
        users[0]['2fa_code'] = '123456'
        new_user = {
            'user': 'test_user',
            'phone': '123456789',
            'balance': '1000.00',
            '2fa_code': ''
        }
        users.append(new_user)        #Writeusers
        write_users(users)
        updated_users = read_users()
        self.assertEqual(len(updated_users), 2)
        self.assertEqual(updated_users[0]['balance'], '3000.00')
        self.assertEqual(updated_users[0]['2fa_code'], '123456')
        self.assertEqual(updated_users[1]['user'], 'test_user')
        self.assertEqual(updated_users[1]['phone'], '123456789')
    def test_append_log(self):
        ensure_files()
        append_log('test_user', 'Deposit', 100.50, 1500.75)
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            logs = list(reader)
        self.assertEqual(len(logs), 1)
        self.assertEqual(logs[0]['user'], 'test_user')
        self.assertEqual(logs[0]['action'], 'Deposit')
        self.assertEqual(logs[0]['amount'], '100.50')
        self.assertEqual(logs[0]['balance_after'], '1500.75')
        self.assertIn('timestamp', logs[0])
        append_log('test_user', 'Withdraw', 50.25, 1450.50)
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            logs = list(reader)
        self.assertEqual(len(logs), 2)
        self.assertEqual(logs[1]['action'], 'Withdraw')
        self.assertEqual(logs[1]['amount'], '50.25')
        self.assertEqual(logs[1]['balance_after'], '1450.50')
if __name__ == '__main__':
    unittest.main()

