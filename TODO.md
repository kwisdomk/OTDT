# OTDT React Dashboard: Fix Asset ID

**✅ Step 1: Create/Update TODO.md** - Done

**✅ Step 2: Edit frontend App.js**  
- Change asset_id from 'WP-07' → 'GDC-WP-007'  
- Update fallback message  
- Fixed indentation  
- Clean final rewrite

**✅ Step 3: Test the fix**  
- Refresh http://localhost:3000  
- Verify turbine data displays (sensors, failure probability, status)  
- Test anomaly demo: simulator --demo, watch yellow/red at t=60s  
- Check work order creation when prob > 0.25  

**✅ Step 4: Verify integration**  
- WebSocket connected (green status)  
- Monte Carlo triggered on anomaly  
- Maximo mock work order appears  

**⏳ Step 5: Commit changes**  
- git add .  
- git commit -m "fix: react dashboard asset ID to GDC-WP-007"  
- git push  

**✅ Step 6: Complete task & update progress**  
- Dashboard Phase 5 → 100% ✅  
- Overall progress: 90%  
- Ready for Unity XR (Phase 6)
