"""
Script to create a .env file with secure keys if it doesn't exist.
This ensures JWT_SECRET_KEY persists across server restarts.
"""
import os
import secrets
from pathlib import Path

def generate_secret_key():
    """Generate a secure random secret key"""
    return secrets.token_urlsafe(32)

def create_env_file():
    """Create .env file with secure keys if it doesn't exist"""
    env_path = Path(__file__).parent / '.env'
    env_example_path = Path(__file__).parent / 'env.example'
    
    if env_path.exists():
        print("✅ .env file already exists")
        # Check if JWT_SECRET_KEY is set
        with open(env_path, 'r') as f:
            content = f.read()
            if 'JWT_SECRET_KEY=' in content:
                print("✅ JWT_SECRET_KEY is already set in .env")
                return
            else:
                print("⚠️  JWT_SECRET_KEY not found in .env, adding it...")
                # Read existing content
                existing_content = content
    else:
        print("📝 Creating new .env file...")
        existing_content = ""
        # If env.example exists, use it as a template
        if env_example_path.exists():
            with open(env_example_path, 'r') as f:
                existing_content = f.read()
    
    # Generate secure keys
    secret_key = generate_secret_key()
    jwt_secret_key = generate_secret_key()
    
    # Prepare .env content
    env_content = existing_content
    
    # Add or update SECRET_KEY
    if 'SECRET_KEY=' not in env_content:
        env_content += f"\nSECRET_KEY={secret_key}\n"
    else:
        # Update existing SECRET_KEY if it's the default
        lines = env_content.split('\n')
        updated_lines = []
        for line in lines:
            if line.startswith('SECRET_KEY='):
                if 'change-in-production' in line or 'your-secret-key' in line:
                    updated_lines.append(f'SECRET_KEY={secret_key}')
                else:
                    updated_lines.append(line)
            else:
                updated_lines.append(line)
        env_content = '\n'.join(updated_lines)
    
    # Add or update JWT_SECRET_KEY
    if 'JWT_SECRET_KEY=' not in env_content:
        env_content += f"JWT_SECRET_KEY={jwt_secret_key}\n"
    else:
        # Update existing JWT_SECRET_KEY if it's the default
        lines = env_content.split('\n')
        updated_lines = []
        for line in lines:
            if line.startswith('JWT_SECRET_KEY='):
                if 'change-in-production' in line or 'your-jwt-secret-key' in line:
                    updated_lines.append(f'JWT_SECRET_KEY={jwt_secret_key}')
                else:
                    updated_lines.append(line)
            else:
                updated_lines.append(line)
        env_content = '\n'.join(updated_lines)
    
    # Ensure DATABASE_URL is set
    if 'DATABASE_URL=' not in env_content:
        env_content += "DATABASE_URL=postgresql://postgres:postgres@localhost:5432/smartbiz360\n"
    
    # Write .env file
    with open(env_path, 'w') as f:
        f.write(env_content)
    
    print("✅ .env file created/updated successfully!")
    print("✅ Secure JWT_SECRET_KEY has been generated and saved")
    print(f"📁 Location: {env_path.absolute()}")
    print("\n⚠️  IMPORTANT: Keep your .env file secure and never commit it to version control!")

if __name__ == '__main__':
    create_env_file()

