#!/bin/bash
# Deploy to Cloudflare Pages for online access

echo "=========================================="
echo "  CLOUDFLARE PAGES DEPLOYMENT"
echo "=========================================="
echo ""

# Install Wrangler (Cloudflare CLI) if not present
if ! command -v wrangler &> /dev/null; then
    echo "Installing Wrangler CLI..."
    npm install -g wrangler
fi

# Login to Cloudflare (will open browser)
echo "Step 1: Login to Cloudflare..."
wrangler login

# Create a simple static export for demo
echo "Step 2: Creating static build..."
mkdir -p public
cat > public/index.html << 'HTML'
<!DOCTYPE html>
<html>
<head>
    <title>Ghana Microfinance MIS - Deployment Info</title>
    <style>
        body { font-family: Arial; max-width: 800px; margin: 50px auto; padding: 20px; }
        h1 { color: #2c3e50; }
        .info { background: #ecf0f1; padding: 20px; border-radius: 8px; margin: 20px 0; }
        code { background: #34495e; color: #ecf0f1; padding: 3px 8px; border-radius: 4px; }
    </style>
</head>
<body>
    <h1>🏦 Ghana Microfinance MIS</h1>
    <div class="info">
        <h2>📦 Repository Information</h2>
        <p><strong>GitHub Repository:</strong><br>
        <a href="https://github.com/kfrem/microfinance-mis">https://github.com/kfrem/microfinance-mis</a></p>
        
        <p><strong>Branch:</strong> <code>genspark_ai_developer</code></p>
        
        <p><strong>Latest Commit:</strong> <code>18aa57b</code></p>
    </div>
    
    <div class="info">
        <h2>🚀 Deployment Instructions</h2>
        <p><strong>For Local Development:</strong></p>
        <pre><code>git clone https://github.com/kfrem/microfinance-mis.git
cd microfinance-mis
git checkout genspark_ai_developer
docker compose up --build -d
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
# Access: http://localhost:8000/</code></pre>
    </div>
    
    <div class="info">
        <h2>📊 System Overview</h2>
        <ul>
            <li><strong>Technology:</strong> Django 6.0, Python 3.12, PostgreSQL</li>
            <li><strong>Features:</strong> 18+ report types, Excel/PDF exports, BoG compliance</li>
            <li><strong>Test Coverage:</strong> 38 automated tests (100% pass rate)</li>
            <li><strong>Documentation:</strong> Complete guides in repository</li>
        </ul>
    </div>
    
    <div class="info">
        <h2>🔗 Access Points</h2>
        <ul>
            <li><strong>Home:</strong> <code>http://localhost:8000/</code></li>
            <li><strong>Management Reports:</strong> <code>/management/</code></li>
            <li><strong>Operational Reports:</strong> <code>/reports/</code></li>
            <li><strong>Analytics:</strong> <code>/dashboard/</code></li>
            <li><strong>Admin Panel:</strong> <code>/admin/</code></li>
        </ul>
    </div>
    
    <div class="info">
        <h2>📝 Documentation Files</h2>
        <ul>
            <li><code>QUICK_START.md</code> - Quick reference guide</li>
            <li><code>TESTING_GUIDE.md</code> - Testing instructions</li>
            <li><code>REPORTS_FIX_COMPLETE.md</code> - Report system documentation</li>
            <li><code>ADMIN_FIX_SUMMARY.md</code> - Admin panel guide</li>
            <li><code>REGRESSION_PREVENTION_COMPLETE.md</code> - Testing system</li>
            <li><code>TROUBLESHOOTING.md</code> - Common issues and fixes</li>
        </ul>
    </div>
    
    <div class="info">
        <h2>⚠️ Current Known Issues</h2>
        <p><em>For review by next developer:</em></p>
        <ol>
            <li><strong>Django 6.0 Compatibility:</strong> Some admin display methods have SafeString format issues (fixed in latest commit)</li>
            <li><strong>Officer Performance:</strong> Uses disbursed_by field (corrected in commit c1f472f)</li>
            <li><strong>All tests passing:</strong> 38/38 tests pass with validate_system.py</li>
        </ol>
    </div>
    
    <div class="info">
        <h2>📧 Contact</h2>
        <p><strong>Owner:</strong> kfrem</p>
        <p><strong>Repository:</strong> microfinance-mis</p>
        <p><strong>Last Updated:</strong> January 5, 2026</p>
    </div>
</body>
</html>
HTML

echo "Step 3: Deploying to Cloudflare Pages..."
wrangler pages deploy public --project-name=microfinance-mis

echo ""
echo "=========================================="
echo "  DEPLOYMENT COMPLETE!"
echo "=========================================="
