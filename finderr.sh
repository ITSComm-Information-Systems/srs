python3 - <<'EOF'
import warnings
warnings.filterwarnings("error", category=RuntimeWarning)
import django
django.setup()
EOF

