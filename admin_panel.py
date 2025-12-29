import json, os
from datetime import datetime

class AdminPanel:
    def __init__(self, db='aegis_users.json'):
        self.db = db
        self.load()

    def load(self):
        if os.path.exists(self.db):
            with open(self.db, 'r', encoding='utf-8') as f:
                self.d = json.load(f)
                if 'blocked_users' not in self.d: self.d['blocked_users'] = {}
        else:
            self.d = {'users': {}, 'stats': {'analyzes': 0, 'threats': 0}, 'blocked_users': {}}
            self.save()

    def save(self):
        with open(self.db, 'w', encoding='utf-8') as f: json.dump(self.d, f, ensure_ascii=False, indent=2)

    def add_user(self, uid, username, first_name):
        uid = str(uid)
        if uid in self.d['blocked_users']: return False
        if uid not in self.d['users']:
            self.d['users'][uid] = {'user_id': uid, 'username': username, 'name': first_name, 'joined': str(datetime.now()), 'analyzes': 0}
            self.save()
        return True

    def log_analysis(self, uid, threat):
        uid = str(uid)
        if uid in self.d['users']: self.d['users'][uid]['analyzes'] += 1
        self.d['stats']['analyzes'] += 1
        if threat: self.d['stats']['threats'] += 1
        self.save()

    def delete_user(self, uid):
        if str(uid) in self.d['users']: del self.d['users'][str(uid)]; self.save()

    def get_user(self, uid): return self.d['users'].get(str(uid))

    def get_stats(self):
        return {'users': len(self.d['users']), 'analyzes': self.d['stats']['analyzes'], 'threats': self.d['stats']['threats'], 'blocked_users': len(self.d['blocked_users'])}

    def block_user(self, uid, reason="Ban"):
        self.d['blocked_users'][str(uid)] = {'user_id': uid, 'reason': reason, 'date': str(datetime.now())}
        self.save()

    def unblock_user(self, uid):
        if str(uid) in self.d['blocked_users']: del self.d['blocked_users'][str(uid)]; self.save()

    def is_blocked(self, uid): return str(uid) in self.d['blocked_users']

    def get_blocked_users(self): return list(self.d['blocked_users'].values())

    def get_admin_report(self):
        s = self.get_stats()
        return {'summary': {'total_users': s['users'], 'total_analyzes': s['analyzes'], 'threats_detected': s['threats'], 'blocked_users': s['blocked_users']}}
