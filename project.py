import random
import time
import os
import string
import hashlib
import json
import logging

# Configure logging (daily rotating logs)
logging.basicConfig(
    level=logging.INFO,
    filename=f"fim_{time.strftime('%Y%m%d')}.log",
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def create_test_directory():
    """Create a test directory with files for testing the FIM system."""
    test_dir = "test_directory"
    if not os.path.exists(test_dir):
        os.makedirs(test_dir)
        print(f"Created test directory: {test_dir}")

    # Create subdirectories
    subdirs = ["configs", "logs", "data"]
    for subdir in subdirs:
        subdir_path = os.path.join(test_dir, subdir)
        if not os.path.exists(subdir_path):
            os.makedirs(subdir_path)
            print(f"Created subdirectory: {subdir_path}")

    # Create sample configuration files
    config_files = [
        {"name": "database.cfg", "content": "DB_HOST=localhost\nDB_PORT=3306\nDB_USER=safebank\nDB_PASS=securepassword\n"},
        {"name": "api.cfg", "content": "API_KEY=sk_test_12345\nAPI_TIMEOUT=30\nAPI_VERSION=v2\n"},
        {"name": "security.cfg", "content": "ENCRYPTION=AES256\nSSL_ENABLED=true\nFIREWALL_ACTIVE=true\n"}
    ]
    for config in config_files:
        file_path = os.path.join(test_dir, "configs", config["name"])
        with open(file_path, "w") as f:
            f.write(config["content"])
        print(f"Created config file: {file_path}")

    # Create sample log files
    log_files = [
        {"name": "application.log", "lines": 20},
        {"name": "transactions.log", "lines": 15},
        {"name": "security.log", "lines": 10}
    ]
    for log in log_files:
        file_path = os.path.join(test_dir, "logs", log["name"])
        with open(file_path, "w") as f:
            for i in range(log["lines"]):
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                level = random.choice(["INFO", "DEBUG", "WARNING", "ERROR"])
                message = ''.join(random.choices(string.ascii_letters + string.digits, k=30))
                f.write(f"{timestamp} [{level}] - {message}\n")
        print(f"Created log file: {file_path}")

    # Create sample data files
    data_files = [
        {"name": "customers.csv", "rows": 10},
        {"name": "transactions.csv", "rows": 15},
        {"name": "accounts.csv", "rows": 8}
    ]
    for data in data_files:
        file_path = os.path.join(test_dir, "data", data["name"])
        with open(file_path, "w") as f:
            if "customers" in data["name"]:
                f.write("id,name,email,account_number,balance\n")
                for i in range(data["rows"]):
                    customer_id = i + 1
                    name = f"Customer {customer_id}"
                    email = f"customer{customer_id}@example.com"
                    account = ''.join(random.choices(string.digits, k=10))
                    balance = round(random.uniform(1000, 50000), 2)
                    f.write(f"{customer_id},{name},{email},{account},{balance}\n")
            elif "transactions" in data["name"]:
                f.write("id,date,from_account,to_account,amount,status\n")
                for i in range(data["rows"]):
                    trans_id = i + 1
                    date = time.strftime("%Y-%m-%d")
                    from_acc = ''.join(random.choices(string.digits, k=10))
                    to_acc = ''.join(random.choices(string.digits, k=10))
                    amount = round(random.uniform(10, 5000), 2)
                    status = random.choice(["completed", "pending", "failed"])
                    f.write(f"{trans_id},{date},{from_acc},{to_acc},{amount},{status}\n")
            elif "accounts" in data["name"]:
                f.write("account_number,type,status,created_date,last_activity\n")
                for i in range(data["rows"]):
                    account = ''.join(random.choices(string.digits, k=10))
                    acc_type = random.choice(["savings", "checking", "investment"])
                    status = random.choice(["active", "inactive", "suspended"])
                    created = time.strftime("%Y-%m-%d", time.gmtime(time.time() - random.randint(0, 365 * 24 * 3600)))
                    activity = time.strftime("%Y-%m-%d", time.gmtime(time.time() - random.randint(0, 30 * 24 * 3600)))
                    f.write(f"{account},{acc_type},{status},{created},{activity}\n")
        print(f"Created data file: {file_path}")

    print("\nTest environment setup complete. Use these files to test the FIM system.")

def calculate_hash(file_path):
    """Calculate SHA-256 hash of a file with error handling."""
    try:
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except (OSError, PermissionError) as e:
        logging.error(f"Failed to read {file_path}: {e}")
        return None

def find_files(directory):
    """Recursively find all files in a directory."""
    file_list = []
    for root, _, files in os.walk(directory):
        for file in files:
            file_list.append(os.path.join(root, file))
    return file_list

def create_baseline(directory):
    """Create a baseline of file hashes with timestamping."""
    os.makedirs("baselines", exist_ok=True)  # Ensure dir exists
    files = find_files(directory)
    baseline = {}
    for file in files:
        file_hash = calculate_hash(file)
        if file_hash:  # Only add if hash was computed successfully
            baseline[file] = file_hash
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    baseline_file = os.path.join("baselines", f"baseline_{timestamp}.json")
    with open(baseline_file, 'w') as f:
        json.dump(baseline, f, indent=4)  # Pretty-print JSON
    logging.info(f"Baseline created with {len(baseline)} files. Saved to {baseline_file}")
    return baseline_file

if __name__ == "__main__":
    create_test_directory()  # Step 1: Create test files
    monitored_dir = "test_directory"  # Step 2: Monitor the test dir
    create_baseline(monitored_dir)  # Step 3: Create baseline