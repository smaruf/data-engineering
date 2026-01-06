# 🚀 Getting Started Guide

Complete step-by-step guide to start your Snowflake and Databricks mastery journey.

## 📋 Prerequisites Checklist

### Required
- [ ] Computer with internet connection
- [ ] Python 3.8 or higher installed
- [ ] Basic understanding of:
  - [ ] Python programming
  - [ ] SQL queries
  - [ ] Command line interface
  - [ ] Git basics

### Recommended
- [ ] Understanding of data engineering concepts
- [ ] Familiarity with cloud platforms (AWS/Azure/GCP)
- [ ] Experience with Jupyter notebooks
- [ ] Basic understanding of distributed systems

## 🎯 Step 1: Account Setup

### Snowflake Account

1. **Sign up for free trial**
   - Visit: https://signup.snowflake.com/
   - Choose cloud provider (AWS, Azure, or GCP)
   - Select region closest to you
   - No credit card required for 30-day trial
   - $400 in free credits

2. **After signup**
   - Check your email for activation link
   - Set your password
   - Note your account identifier (in the URL)
   - Example: `xy12345.us-east-1.snowflakecomputing.com`

3. **First login**
   - Explore the web interface (Snowsight)
   - Navigate to Worksheets
   - Try a simple query: `SELECT CURRENT_VERSION();`

### Databricks Account

**Option A: Community Edition (Recommended for learning)**

1. **Sign up**
   - Visit: https://community.cloud.databricks.com/login.html
   - Click "Sign up" 
   - Use your email address
   - Free tier (no credit card needed)

2. **After signup**
   - Verify your email
   - Access your workspace
   - Explore the interface
   - Free cluster with limited resources

**Option B: Cloud Provider Databricks**

1. **Through cloud provider**
   - AWS: https://aws.amazon.com/marketplace/pp/B07M64T7KP
   - Azure: https://azuremarketplace.microsoft.com/en-us/marketplace/apps/databricks.databricks
   - GCP: https://console.cloud.google.com/marketplace/product/databricks-prod/databricks

2. **Benefits**
   - More resources
   - Production capabilities
   - Full feature access
   - Requires cloud account

## 🔧 Step 2: Local Environment Setup

### 1. Clone Repository

```bash
# Clone the repository
git clone https://github.com/smaruf/data-engineering.git

# Navigate to project
cd data-engineering/snowflake-databricks-mastery
```

### 2. Python Environment Setup

**Using venv (recommended):**

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip
```

**Using conda (alternative):**

```bash
# Create conda environment
conda create -n snowflake-databricks python=3.10

# Activate environment
conda activate snowflake-databricks
```

### 3. Install Dependencies

```bash
# Install all required packages
pip install -r requirements.txt

# Verify installation
python -c "import snowflake.connector; print('Snowflake OK')"
python -c "import pyspark; print('PySpark OK')"
```

### 4. Environment Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your credentials
# On Windows:
notepad .env
# On macOS/Linux:
nano .env
# Or use your preferred editor
```

**Configure your .env file:**

```env
# Snowflake Configuration
SNOWFLAKE_ACCOUNT=your_account_identifier
SNOWFLAKE_USER=your_username
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_WAREHOUSE=COMPUTE_WH
SNOWFLAKE_DATABASE=DEMO_DB
SNOWFLAKE_SCHEMA=PUBLIC

# Databricks Configuration (optional for local PySpark)
DATABRICKS_HOST=https://your-workspace.cloud.databricks.com
DATABRICKS_TOKEN=your_access_token
DATABRICKS_CLUSTER_ID=your_cluster_id
```

## ✅ Step 3: Verify Installation

### Test Snowflake Connection

```bash
cd beginner/snowflake
python 01_setup_connection.py
```

Expected output:
```
✅ Successfully connected to Snowflake!
   Account: your_account
   Database: DEMO_DB
   Schema: PUBLIC
```

### Test Databricks/PySpark

```bash
cd beginner/databricks
python 01_setup_connection.py
```

Expected output:
```
✅ Local Spark session created successfully!
   Spark Version: 3.5.0
```

## 📚 Step 4: Start Learning

### Week 1-2: Beginner Level

**Day 1-3: Snowflake Basics**
```bash
cd beginner/snowflake
python 01_setup_connection.py
python 02_basic_operations.py
python 03_data_loading.py
```

**Day 4-6: Databricks Basics**
```bash
cd beginner/databricks
python 01_setup_connection.py
python 02_dataframe_basics.py
python 03_read_write_data.py
```

**Day 7: Review and Practice**
- Review all examples
- Modify code with your own data
- Complete practice exercises

### Week 3-4: Intermediate Level

**Snowflake Intermediate**
- Snowpipe and automation
- Streams and Tasks
- Time Travel
- Data sharing

**Databricks Intermediate**
- Delta Lake
- Structured Streaming
- MLflow basics
- Performance optimization

### Week 5-6: Advanced Level

**Advanced Topics**
- Snowpark Python
- Unity Catalog
- AutoML
- Production patterns

### Week 7-8: Expert Level

**Integration and Best Practices**
- Combined architectures
- Real-world projects
- Production deployment

## 🎓 Learning Tips

### Best Practices

1. **Consistency is Key**
   - Study 1-2 hours daily
   - Better than 8 hours once a week
   - Build habit and muscle memory

2. **Hands-On Practice**
   - Run every example
   - Modify code to understand it better
   - Break things and fix them
   - Create your own projects

3. **Take Notes**
   - Document what you learn
   - Create personal cheat sheets
   - Write blog posts to solidify knowledge

4. **Ask Questions**
   - Use community forums
   - Stack Overflow
   - GitHub issues
   - LinkedIn groups

### Study Techniques

1. **The 50/50 Rule**
   - 50% learning/watching
   - 50% building/practicing

2. **Spaced Repetition**
   - Review concepts after 1 day, 1 week, 1 month
   - Reinforces long-term memory

3. **Project-Based Learning**
   - Build real projects
   - Solve actual problems
   - Portfolio development

## 🛠️ Optional Tools

### IDEs and Editors

**VS Code (Recommended)**
```bash
# Install VS Code
# Download from: https://code.visualstudio.com/

# Install extensions:
- Python
- Snowflake
- Databricks
- Jupyter
- GitLens
```

**JetBrains DataGrip**
- Database management
- SQL development
- Great for Snowflake

**Jupyter Lab**
```bash
# Already in requirements.txt
# Start Jupyter Lab
jupyter lab

# Or use Docker
docker-compose up jupyter
```

### Command Line Tools

**SnowSQL** (Snowflake CLI)
```bash
# Download and install
# Visit: https://docs.snowflake.com/en/user-guide/snowsql-install-config.html

# Configure
snowsql -a your_account -u your_username
```

**Databricks CLI**
```bash
# Already in requirements.txt
# Configure
databricks configure --token

# Enter host and token when prompted
```

## 🚨 Troubleshooting

### Common Issues

**Issue: Cannot connect to Snowflake**
```
Solution:
1. Verify account identifier is correct
2. Check username and password
3. Ensure warehouse exists
4. Check firewall/VPN settings
```

**Issue: PySpark won't start**
```
Solution:
1. Verify Java is installed (Java 8 or 11)
   java -version
2. Set JAVA_HOME environment variable
3. Reinstall PySpark
   pip install --upgrade pyspark
```

**Issue: Module not found errors**
```
Solution:
1. Verify virtual environment is activated
2. Reinstall requirements
   pip install -r requirements.txt
3. Check Python version (3.8+)
```

**Issue: Permission denied errors**
```
Solution:
1. Run as administrator/sudo if needed
2. Check file permissions
3. Verify write access to directories
```

## 📞 Getting Help

### Resources

1. **This Repository**
   - Check README files
   - Review code comments
   - Open GitHub issues

2. **Official Documentation**
   - Snowflake: https://docs.snowflake.com/
   - Databricks: https://docs.databricks.com/

3. **Community Forums**
   - Snowflake Community
   - Databricks Community
   - Stack Overflow
   - Reddit r/dataengineering

4. **Learning Resources**
   - See [docs/resources.md](resources.md)
   - Free courses and tutorials
   - Books and videos

## 🎯 Success Metrics

Track your progress:

### Week 2 Checkpoint
- [ ] Can connect to both platforms
- [ ] Understand basic CRUD operations
- [ ] Can load and query data
- [ ] Comfortable with DataFrames

### Week 4 Checkpoint
- [ ] Built first ETL pipeline
- [ ] Understand Delta Lake
- [ ] Can use Snowpipe
- [ ] Comfortable with streaming

### Week 8 Checkpoint
- [ ] Completed all levels
- [ ] Built capstone project
- [ ] Ready for certification
- [ ] Can build production systems

## 🎓 Next Steps After Completion

1. **Certifications**
   - SnowPro Core
   - Databricks Certified Data Engineer

2. **Build Portfolio**
   - GitHub projects
   - Blog posts
   - YouTube tutorials

3. **Job Search**
   - Update LinkedIn
   - Apply to positions
   - Network with professionals

4. **Continuous Learning**
   - Stay updated with new features
   - Join communities
   - Contribute to open source

---

**Ready to start? Begin with beginner/snowflake/01_setup_connection.py!**

Good luck on your learning journey! 🚀
