"""
Quick start script to help set up and run the system.
"""
import subprocess
import sys
import os


def run_command(cmd: str, description: str):
    """Run a shell command."""
    print(f"\n{'='*60}")
    print(f"🔧 {description}")
    print(f"{'='*60}")
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        print(f"❌ Failed: {description}")
        sys.exit(1)
    print(f"✅ Completed: {description}")


def main():
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║   Hospital Multi-Domain Chat System - Quick Start        ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    
    # Check environment
    if not os.path.exists('.env'):
        print("⚠️  No .env file found. Creating from template...")
        subprocess.run("cp .env.example .env", shell=True)
        print("📝 Please edit .env with your GCP project details")
        print("   Then run this script again.")
        sys.exit(0)
    
    print("Select an option:")
    print("1. Install dependencies")
    print("2. Set up GCP infrastructure (buckets + datastores)")
    print("3. Ingest documents from buckets")
    print("4. Run API server locally")
    print("5. Run tests")
    print("6. Deploy to Cloud Run")
    print("7. Full setup (2 + 3)")
    print("0. Exit")
    
    choice = input("\nEnter choice (0-7): ").strip()
    
    if choice == "1":
        run_command("pip install -r requirements.txt", "Installing dependencies")
    
    elif choice == "2":
        run_command("python scripts/setup_buckets.py --all", "Creating GCS buckets")
        run_command("python scripts/setup_datastores.py --all", "Creating Vertex AI Search datastores")
        print("\n📤 Next step: Upload documents to GCS buckets")
        print("   Use: gsutil cp -r /path/to/docs gs://bucket-name/")
    
    elif choice == "3":
        run_command("python scripts/ingest_documents.py --all", "Ingesting documents")
    
    elif choice == "4":
        print("\n🚀 Starting API server on http://localhost:8080")
        print("   Press Ctrl+C to stop")
        subprocess.run("python src/main.py", shell=True)
    
    elif choice == "5":
        run_command("python tests/test_api.py", "Running integration tests")
    
    elif choice == "6":
        run_command("chmod +x scripts/deploy.sh && ./scripts/deploy.sh", "Deploying to Cloud Run")
    
    elif choice == "7":
        run_command("python scripts/setup_buckets.py --all", "Creating GCS buckets")
        run_command("python scripts/setup_datastores.py --all", "Creating datastores")
        print("\n📤 Upload documents to buckets, then press Enter to continue...")
        input()
        run_command("python scripts/ingest_documents.py --all", "Ingesting documents")
    
    elif choice == "0":
        print("👋 Goodbye!")
        sys.exit(0)
    
    else:
        print("❌ Invalid choice")
        sys.exit(1)
    
    print("\n✨ Done!")


if __name__ == "__main__":
    main()
