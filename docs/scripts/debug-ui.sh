#!/bin/bash

# Dashboard UI Debug Script
# Tests dashboard interface functionality

DASHBOARD_URL="http://localhost:5002"

echo "🔍 Dashboard UI Debug Report"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Test main page
echo "1. Main Page Access:"
main_response=$(curl -s -o /dev/null -w "%{http_code}:%{time_total}" "$DASHBOARD_URL/")
echo "   Status: $(echo $main_response | cut -d':' -f1)"
echo "   Load time: $(echo $main_response | cut -d':' -f2)s"

# Test static files
echo ""
echo "2. Static Files:"
css_response=$(curl -s -o /dev/null -w "%{http_code}" "$DASHBOARD_URL/static/css/dashboard.css")
js_response=$(curl -s -o /dev/null -w "%{http_code}" "$DASHBOARD_URL/static/js/dashboard.js")
echo "   CSS: $css_response"
echo "   JavaScript: $js_response"

# Test API endpoints used by frontend
echo ""
echo "3. API Endpoints:"
health_response=$(curl -s -o /dev/null -w "%{http_code}" "$DASHBOARD_URL/api/health")
status_response=$(curl -s -o /dev/null -w "%{http_code}" "$DASHBOARD_URL/api/status")
metrics_response=$(curl -s -o /dev/null -w "%{http_code}" "$DASHBOARD_URL/api/metrics")

echo "   /api/health: $health_response"
echo "   /api/status: $status_response" 
echo "   /api/metrics: $metrics_response"

# Check for JavaScript syntax errors
echo ""
echo "4. JavaScript Validation:"
js_content=$(curl -s "$DASHBOARD_URL/static/js/dashboard.js")

# Check for common issues
if echo "$js_content" | grep -q "class Dashboard"; then
    echo "   ✅ Dashboard class found"
else
    echo "   ❌ Dashboard class missing"
fi

if echo "$js_content" | grep -q "setupNavigation"; then
    echo "   ✅ Navigation setup found"
else
    echo "   ❌ Navigation setup missing"
fi

if echo "$js_content" | grep -q "DOMContentLoaded"; then
    echo "   ✅ DOM initialization found"
else
    echo "   ❌ DOM initialization missing"
fi

if echo "$js_content" | grep -q "addEventListener"; then
    echo "   ✅ Event listeners found"
else
    echo "   ❌ Event listeners missing"
fi

# Check HTML structure
echo ""
echo "5. HTML Structure:"
html_content=$(curl -s "$DASHBOARD_URL/")

if echo "$html_content" | grep -q 'data-section="overview"'; then
    echo "   ✅ Navigation items with data-section found"
else
    echo "   ❌ Navigation items missing data-section attributes"
fi

if echo "$html_content" | grep -q 'id="overview"'; then
    echo "   ✅ Section containers found"
else
    echo "   ❌ Section containers missing"
fi

if echo "$html_content" | grep -q 'class="content-section active"'; then
    echo "   ✅ Active section class found"
else
    echo "   ❌ Active section class missing"
fi

# Check CSS for navigation styles
echo ""
echo "6. CSS Navigation Styles:"
css_content=$(curl -s "$DASHBOARD_URL/static/css/dashboard.css")

if echo "$css_content" | grep -q "\.content-section"; then
    echo "   ✅ Content section styles found"
else
    echo "   ❌ Content section styles missing"
fi

if echo "$css_content" | grep -q "\.content-section\.active"; then
    echo "   ✅ Active section styles found"
else
    echo "   ❌ Active section styles missing"
fi

if echo "$css_content" | grep -q "\.nav-item"; then
    echo "   ✅ Navigation item styles found"
else
    echo "   ❌ Navigation item styles missing"
fi

# Test JavaScript execution by checking console output
echo ""
echo "7. JavaScript Console Test:"
echo "   Open http://localhost:5002 in browser and check console for errors"
echo "   Expected: Dashboard initialization messages"
echo "   If navigation doesn't work: Check browser console (F12)"

echo ""
echo "8. Manual Testing Steps:"
echo "   1. Open: $DASHBOARD_URL"
echo "   2. Try clicking navigation items (Overview, Services, etc.)"
echo "   3. Check browser console (F12 → Console tab)"
echo "   4. Look for JavaScript errors or warnings"

echo ""
echo "9. Quick Fix Commands:"
echo "   Restart dashboard: docker-compose -f compose.local.yml restart dashboard"
echo "   Clear browser cache: Ctrl+F5 or Cmd+Shift+R"
echo "   Check logs: docker logs open-webui-hub-dashboard-1"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Debug complete. If navigation still doesn't work,"
echo "open browser developer tools (F12) and check Console tab."
