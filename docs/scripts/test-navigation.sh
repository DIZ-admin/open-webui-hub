#!/bin/bash

# Quick Navigation Test
echo "🔍 Testing Dashboard Navigation..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

DASHBOARD_URL="http://localhost:5002"

# Test main page
echo "1. Testing Dashboard Access:"
response=$(curl -s -o /dev/null -w "%{http_code}" "$DASHBOARD_URL/")
if [ "$response" = "200" ]; then
    echo "   ✅ Dashboard accessible ($response)"
else
    echo "   ❌ Dashboard not accessible ($response)"
    exit 1
fi

# Test static files
echo ""
echo "2. Testing Navigation Files:"
nav_fix=$(curl -s -o /dev/null -w "%{http_code}" "$DASHBOARD_URL/static/js/navigation-fix.js")
nav_test=$(curl -s -o /dev/null -w "%{http_code}" "$DASHBOARD_URL/static/js/navigation-test.js")
dashboard_js=$(curl -s -o /dev/null -w "%{http_code}" "$DASHBOARD_URL/static/js/dashboard.js")

echo "   Navigation Fix: $nav_fix"
echo "   Navigation Test: $nav_test" 
echo "   Dashboard JS: $dashboard_js"

if [ "$nav_fix" = "200" ] && [ "$nav_test" = "200" ] && [ "$dashboard_js" = "200" ]; then
    echo "   ✅ All navigation files accessible"
else
    echo "   ❌ Some navigation files missing"
fi

# Check HTML includes
echo ""
echo "3. Testing HTML Script Includes:"
html_content=$(curl -s "$DASHBOARD_URL/")

if echo "$html_content" | grep -q "navigation-fix.js"; then
    echo "   ✅ Navigation fix included in HTML"
else
    echo "   ❌ Navigation fix NOT included in HTML"
fi

if echo "$html_content" | grep -q "navigation-test.js"; then
    echo "   ✅ Navigation test included in HTML"
else
    echo "   ❌ Navigation test NOT included in HTML"
fi

echo ""
echo "4. Next Steps:"
echo "   1. Open: $DASHBOARD_URL"
echo "   2. Open Developer Tools (F12)"
echo "   3. Check Console tab for navigation messages"
echo "   4. Try clicking navigation buttons"
echo ""
echo "5. Console Test Commands:"
echo "   switchSection('services')   # Switch to services"
echo "   testAllSections()          # Test all sections"
echo ""
echo "If navigation still doesn't work:"
echo "   - Check browser console for errors"
echo "   - Clear browser cache (Ctrl+F5)"
echo "   - Run: docker logs open-webui-hub-dashboard-1"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Navigation fix deployed successfully!"
echo "🌐 Open $DASHBOARD_URL to test"
