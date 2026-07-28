import sys
import os
import psycopg2

def init_ctfd_oauth():
    db_url = os.getenv('DATABASE_URL', 'postgresql://hx_user:hx_secure_password_123!@db:5432/hackerxploit')
    
    try:
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        
        # Check if CTFd config table exists
        cursor.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'config');")
        exists = cursor.fetchone()[0]
        
        if not exists:
            print("CTFd config table does not exist yet. CTFd will create it on first run.")
            return

        oauth_configs = {
            'oauth_client_id': os.getenv('CTFD_OAUTH_CLIENT_ID', 'ctfd-client-id-hx99'),
            'oauth_client_secret': os.getenv('CTFD_OAUTH_CLIENT_SECRET', 'ctfd-client-secret-sec88'),
            'oauth_authorization_endpoint': os.getenv('CTFD_OAUTH_AUTH_URL', 'http://hackerxploit.org/oauth/authorize'),
            'oauth_token_endpoint': os.getenv('CTFD_OAUTH_TOKEN_URL', 'http://web:5000/oauth/token'),
            'oauth_api_endpoint': os.getenv('CTFD_OAUTH_API_URL', 'http://web:5000/oauth/userinfo')
        }

        for key, value in oauth_configs.items():
            cursor.execute("""
                INSERT INTO config (key, value)
                VALUES (%s, %s)
                ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value;
            """, (key, value))

        conn.commit()
        cursor.close()
        conn.close()
        print("Successfully initialized CTFd OAuth2 configuration in CTFd database!")

    except Exception as e:
        print(f"CTFd OAuth initialization note: {e}")

if __name__ == '__main__':
    init_ctfd_oauth()
