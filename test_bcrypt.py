from passlib.context import CryptContext

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
hash_val = '$2b$12$4aDHxIhYefT1QkXIxdiMoeW99j1P3t6ML3R62jNbvh6OjGso5WkSy'
password = 'SecurePass123!'

print(f'Password length: {len(password)}')
print(f'Hash: {hash_val}')
print(f'Hash length: {len(hash_val)}')

try:
    result = pwd_context.verify(password, hash_val)
    print(f'✅ Verification result: {result}')
except Exception as e:
    print(f'❌ Error: {type(e).__name__}: {e}')
