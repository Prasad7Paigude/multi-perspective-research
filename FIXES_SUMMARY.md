# Fixes Summary for Analyst Perspectives and Thinking Display Issues

## Issues Identified

### Issue 1: "1 analyst perspectives" shown instead of actual count
**Root Cause**: In `FinalReport.tsx`, the component was displaying `sections.length` instead of the actual number of analysts.

**Fix Applied**:
- Updated `FinalReport.tsx` to accept an `analysts` prop
- Changed the display from `{sections.length}` to `{analysts?.length || sections.length}`
- Updated `App.tsx` to pass the `analysts` array to the `FinalReport` component

### Issue 2: Thinking only shown before final result, not throughout interview
**Root Cause**: Multiple problems in the backend and frontend:
1. Backend (`api/server.py`) was emitting `thinking_start` event for EACH thinking text chunk (inside the loop), causing the thinking state to reset multiple times
2. Backend was emitting `interview_start` BEFORE `thinking_start`, which caused the frontend to clear the thinking state
3. Frontend (`useResearch.ts`) was clearing the thinking state on `interview_start` event

**Fix Applied**:
1. **Backend (`api/server.py`)**:
   - Moved `interview_start` event to emit BEFORE `thinking_start` (but with proper analyst info)
   - Changed to emit `thinking_start` ONCE per analyst (outside the thinking_texts loop)
   - Emit all thinking chunks for that analyst
   - Emit `thinking_complete` ONCE per analyst (outside the thinking_texts loop)
   - Added analyst name and role to the `interview_start` payload

2. **Frontend (`useResearch.ts`)**:
   - Changed `interview_start` case to UPDATE the thinking state with new analyst info instead of clearing it
   - This ensures thinking is shown continuously from when analysts are selected until the final result

## Files Modified

1. **api/server.py** - Fixed thinking event emission logic
   - Lines 241-272: Restructured to emit thinking_start once per analyst, not per chunk
   - Added analyst info to interview_start payload

2. **frontend/src/hooks/useResearch.ts** - Fixed thinking state handling
   - Line 167: Changed from clearing thinking state to updating it with new analyst info

3. **frontend/src/components/FinalReport.tsx** - Fixed analyst count display
   - Added `analysts` prop to component interface
   - Changed display to use `analysts?.length || sections.length`

4. **frontend/src/App.tsx** - Pass analysts to FinalReport
   - Added `analysts={analysts}` prop to FinalReport component

## Expected Behavior After Fixes

1. **Analyst Perspectives Count**: Will now correctly show the number of analysts (e.g., "3 analyst perspectives" for 3 analysts)

2. **Thinking Display**: Will now show thinking continuously:
   - Starts when interview_start is received (with analyst name/role)
   - Continues through all thinking chunks
   - Shows the thinking text streaming in real-time
   - Persists until thinking_complete is received
   - Then updates for the next analyst
   - Continues throughout the entire interview process until final result