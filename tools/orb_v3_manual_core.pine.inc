// Indicator-only confirmed-bar signal engine. Edit this file, then run
// build_orb_v3.py --target manual. The backtest remains on orb_v3_core.pine.inc.
// Objective ICT-style approximations, not proprietary ICT code or probabilities.
// Signal-flow / visibility / retest-depth revision: 2026-09-23.
const string GP = "01 | Research profile"
const string GS = "02 | Sessions (local to each timezone)"
const string GO = "03 | ORB and entry timing"
const string GC = "04 | Confirmation and context"
const string GR = "05 | Risk and estimated levels"
const string GV = "06 | Display and alerts"

string profile = input.string("Auto research candidate", "Profile", options = ["Auto research candidate", "Custom"], group = GP, tooltip = "Exploratory leads from v1 exports, NOT validated settings for this new engine. Gold: M15 NY short; EURUSD: M5 London long; GBPJPY: M5 London short; GBPUSD: M5 London both. Other symbols use Custom inputs.")
string sessionMode = input.string("Profile session", "Sessions to scan", options = ["Profile session", "All enabled sessions"], group = GP)
string customSession = input.string("New York", "Custom / fallback session", options = ["Asian", "London", "New York"], group = GP)
string customTf = input.timeframe("5", "Custom / fallback chart timeframe", group = GP)
bool enforceTf = input.bool(true, "Require profile chart timeframe", group = GP, tooltip = "Does not change the chart. Set the chart interval yourself. Disable to compare other aligned timeframes.")
string directionInput = input.string("Profile", "Allowed direction", options = ["Profile", "Both", "Long only", "Short only"], group = GP)
int testStart = input.time(timestamp("01 Jan 2026 00:00 +0200"), "Start date", group = GP)
int testEnd = input.time(timestamp("31 Dec 2035 23:59 +0200"), "Last signal time (plans stay active)", group = GP)

bool asiaEnabled = input.bool(true, "Asian enabled", group = GS)
string asiaSpec = input.session("0000-0800", "Asian window", group = GS)
string asiaZone = input.string("Europe/London", "Asian timezone", group = GS, tooltip = "Kept compatible with your exports. This is a configurable FX window, not a universal Asian exchange open.")
bool londonEnabled = input.bool(true, "London enabled", group = GS)
string londonSpec = input.session("0900-1700", "London window", group = GS)
string londonZone = input.string("Africa/Johannesburg", "London timezone", group = GS, tooltip = "Your exports used 09:00 SAST, not a DST-adjusted London open. For the latter use 0800-1600 and Europe/London; test separately.")
bool nyEnabled = input.bool(true, "New York enabled", group = GS)
string nySpec = input.session("0800-1700", "New York window", group = GS)
string nyZone = input.string("America/New_York", "New York timezone", group = GS)
bool weekdaysOnly = input.bool(true, "Monday-Friday session starts only", group = GS)

int orbOffset = input.int(0, "Start ORB this many minutes after session open", minval = 0, maxval = 360, group = GO)
int orbMinutes = input.int(30, "ORB duration (minutes)", minval = 1, maxval = 240, group = GO)
string delayMode = input.string("Profile hypothesis", "Entry delay mode", options = ["Profile hypothesis", "Custom"], group = GO)
int customDelay = input.int(0, "Custom minimum delay after session open (minutes)", minval = 0, maxval = 480, group = GO)
bool delayWholeSetup = input.bool(false, "Delay breakout search too", group = GO, tooltip = "Off: a setup may form before the wait ends, but no signal can be issued early. On: require a fresh breakout after the delay as well.")
int lastEntryBuffer = input.int(30, "Stop new signals this many minutes before session end", minval = 1, maxval = 180, group = GO)
int maxSetupBars = input.int(12, "Setup expiry after breakout (bars)", minval = 2, maxval = 100, group = GO)
float breakAtr = input.float(0.05, "Break / continuation buffer (ATR)", minval = 0.0, maxval = 1.0, step = 0.01, group = GO)
float retestPercent = input.float(25.0, "Maximum ORB retest depth (%)", minval = 0.0, maxval = 100.0, step = 5.0, group = GO, tooltip = "How far price may penetrate back inside the broken ORB before reclaiming it. 0% = boundary only; 100% = the full ORB width. The signal candle must still close back outside the range.")
float minOrbAtr = input.float(0.25, "Minimum ORB width (ATR)", minval = 0.0, step = 0.05, group = GO)
float maxOrbAtr = input.float(8.0, "Maximum ORB width (ATR)", minval = 0.5, step = 0.5, group = GO)

string entryModel = input.string("Break + retest + continuation", "Entry model", options = ["Close breakout", "Break + retest", "Break + retest + continuation"], group = GC, tooltip = "Close breakout: signal on a qualifying fresh breakout close. Break + retest: signal on a later qualifying retest close. Continuation: wait for another candle beyond both extremes. All modes use the same range, displacement, risk and delay guards; none is proven best.")
string contextMode = input.string("Required", "Context filter", options = ["Off", "Required"], group = GC, tooltip = "Independent of entry model. Close breakout checks previously confirmed OB/FVG touches on its breakout candle; Fib is unavailable because no later retracement exists. Retest modes check enabled OB/FVG/Fib touches together on the retest candle. Off removes this gate only.")
bool useOb = input.bool(true, "Count order-block context", group = GC)
bool useFvg = input.bool(true, "Count FVG context", group = GC)
bool useFib = input.bool(true, "Count Fibonacci context", group = GC)
int minContext = input.int(2, "Minimum context matches (not probability)", minval = 1, maxval = 3, group = GC)
int structureBars = input.int(10, "Prior structure lookback", minval = 2, maxval = 50, group = GC)
int obSearch = input.int(10, "Last opposing candle search", minval = 1, maxval = 30, group = GC)
int zoneLife = input.int(60, "Maximum zone age (bars)", minval = 3, maxval = 500, group = GC)
float displacementAtr = input.float(0.6, "Displacement body / ATR", minval = 0.0, maxval = 3.0, step = 0.1, group = GC)
float fvgMinAtr = input.float(0.05, "Minimum FVG width / ATR", minval = 0.0, maxval = 1.0, step = 0.01, group = GC)
float fibShallow = input.float(0.50, "Fib retracement lower fraction", minval = 0.0, maxval = 1.0, step = 0.01, group = GC)
float fibDeep = input.float(0.786, "Fib retracement upper fraction", minval = 0.0, maxval = 1.0, step = 0.001, group = GC)
string trendMode = input.string("None", "Trend filter", options = ["None", "Confirmed HTF EMA"], group = GC)
string trendTf = input.timeframe("240", "Trend timeframe (must be higher than chart)", group = GC)
int emaLength = input.int(50, "Trend EMA length", minval = 2, maxval = 300, group = GC)

float manualEquity = input.float(10000.0, "Manual account equity (ZAR)", minval = 1.0, group = GR, tooltip = "Indicator sizing estimate only: update after account changes. Strategy uses actual tester equity and Properties initial capital instead.")
float riskPercent = input.float(1.0, "Risk budget per trade (%)", minval = 0.1, maxval = 10.0, step = 0.1, group = GR)
float rewardRisk = input.float(3.0, "Target reward / risk", minval = 0.5, maxval = 10.0, step = 0.25, group = GR)
string stopModel = input.string("Opposite ORB", "Estimated stop anchor", options = ["Opposite ORB", "Pullback extreme"], group = GR, tooltip = "Pullback extreme uses the qualifying retest candle. For Close breakout, which has no pullback, it uses the breakout candle extreme instead.")
float stopBufferAtr = input.float(0.10, "Stop buffer (ATR)", minval = 0.0, step = 0.05, group = GR)
float minStopAtr = input.float(0.5, "Minimum stop distance (ATR)", minval = 0.0, step = 0.1, group = GR)
float maxStopAtr = input.float(10.0, "Maximum stop distance (ATR)", minval = 0.1, step = 0.5, group = GR)
float leverageCap = input.float(500.0, "Exposure ceiling (leverage)", minval = 1.0, maxval = 500.0, group = GR)
float marginUsage = input.float(25.0, "Maximum equity allocated to margin (%)", minval = 1.0, maxval = 100.0, group = GR, tooltip = "Default leaves a margin reserve. Position size is the smaller of risk-based size and this exposure cap. This is not a risk percentage.")
float brokerStep = input.float(0.0, "Broker quantity step (0 = symbol minimum)", minval = 0.0, group = GR, tooltip = "TradingView quantity units, NOT automatically lots. Verify your broker's contract size and lot step.")
float unitsPerLot = input.float(0.0, "TradingView quantity per broker lot (0 = hide lots)", minval = 0.0, group = GR)
float sizingCostTicks = input.float(0.0, "Extra round-trip cost allowance for sizing (ticks)", minval = 0.0, group = GR, tooltip = "Reduces quantity only; does NOT deduct backtest costs. Also set commission/slippage in Strategy Properties. Broker costs are not known automatically.")
bool showRanges = input.bool(true, "Show current ORB levels", group = GV)
color asiaOrbColor = input.color(color.blue, "Asian ORB line colour", group = GV)
color londonOrbColor = input.color(color.orange, "London ORB line colour", group = GV)
color nyOrbColor = input.color(color.purple, "New York ORB line colour", group = GV)
int orbLineWidth = input.int(2, "ORB line width", minval = 1, maxval = 5, group = GV)
int orbLineTransparency = input.int(10, "ORB line transparency", minval = 0, maxval = 90, group = GV)
color buySignalColor = input.color(color.teal, "BUY signal colour", group = GV)
color sellSignalColor = input.color(color.red, "SELL signal colour", group = GV)
bool showPanel = input.bool(true, "Show status panel", group = GV)
int retainDays = input.int(5, "Keep completed drawings (observed SAST days)", minval = 1, maxval = 30, group = GV)
bool enableAlerts = input.bool(true, "Enable detailed signal alert() calls", group = GV)

string ticker = str.upper(syminfo.ticker)
bool autoProfile = profile == "Auto research candidate"
bool gold = str.contains(ticker, "XAUUSD")
bool euro = str.contains(ticker, "EURUSD")
bool gj = str.contains(ticker, "GBPJPY")
bool gu = str.contains(ticker, "GBPUSD")
bool knownProfile = gold or euro or gj or gu
string profileSession = autoProfile and knownProfile ? (gold ? "New York" : "London") : customSession
string requiredTf = autoProfile and knownProfile ? (gold ? "15" : "5") : customTf
string profileDirection = autoProfile and knownProfile ? (gold or gj ? "Short only" : euro ? "Long only" : "Both") : "Both"
string allowedDirection = directionInput == "Profile" ? profileDirection : directionInput
int delayMinutes = delayMode == "Profile hypothesis" and autoProfile and gold ? 90 : customDelay
float chartSeconds = timeframe.in_seconds()
float atr = ta.atr(14)
[htfClose, htfEma] = request.security(syminfo.tickerid, trendTf, [close[1], ta.ema(close, emaLength)[1]], lookahead = barmerge.lookahead_on)
float quoteToZar = request.currency_rate(syminfo.currency, "ZAR", ignore_invalid_currency = true)
bool closeEntry = entryModel == "Close breakout"
bool requireContext = contextMode == "Required"
int enabledContexts = (useOb ? 1 : 0) + (useFvg ? 1 : 0) + (useFib and not closeEntry ? 1 : 0)
bool tfOk = timeframe.isintraday and chartSeconds >= 60 and chartSeconds <= orbMinutes * 60 and (orbMinutes * 60) % chartSeconds == 0 and (not enforceTf or chartSeconds == timeframe.in_seconds(requiredTf))
bool contextOk = not requireContext or (enabledContexts >= minContext and (closeEntry or not useFib or fibShallow < fibDeep))
bool trendOk = trendMode == "None" or timeframe.in_seconds(trendTf) > chartSeconds
bool configOk = tfOk and contextOk and trendOk and minOrbAtr < maxOrbAtr and minStopAtr < maxStopAtr and testStart < testEnd and chart.is_standard
bool inDates = time >= testStart and time_close <= testEnd
bool bullishMove = close > open and close - open >= atr * displacementAtr and high > low and (close - open) / (high - low) >= 0.5
bool bearishMove = close < open and open - close >= atr * displacementAtr and high > low and (open - close) / (high - low) >= 0.5
float previousHigh = ta.highest(high, structureBars)[1]
float previousLow = ta.lowest(low, structureBars)[1]

type Zone
    float lo = na
    float hi = na
    int born = na
var Zone bullOb = Zone.new()
var Zone bearOb = Zone.new()
var Zone bullFvg = Zone.new()
var Zone bearFvg = Zone.new()
method clear(Zone z) =>
    z.lo := na
    z.hi := na
    z.born := na
method updateZone(Zone z, float lo, float hi) =>
    z.lo := lo
    z.hi := hi
    z.born := bar_index
method overlaps(Zone z, int d) =>
    not na(z.born) and bar_index > z.born and bar_index - z.born <= zoneLife and low <= z.hi and high >= z.lo and (d == 1 ? close >= z.lo : close <= z.hi)

if barstate.isconfirmed
    if not na(bullOb.born) and (close < bullOb.lo or bar_index - bullOb.born > zoneLife)
        bullOb.clear()
    if not na(bearOb.born) and (close > bearOb.hi or bar_index - bearOb.born > zoneLife)
        bearOb.clear()
    if not na(bullFvg.born) and (close < bullFvg.lo or bar_index - bullFvg.born > zoneLife)
        bullFvg.clear()
    if not na(bearFvg.born) and (close > bearFvg.hi or bar_index - bearFvg.born > zoneLife)
        bearFvg.clear()
    if bullishMove and close > previousHigh
        for i = 1 to obSearch
            if close[i] < open[i]
                bullOb.updateZone(low[i], high[i])
                break
    if bearishMove and close < previousLow
        for i = 1 to obSearch
            if close[i] > open[i]
                bearOb.updateZone(low[i], high[i])
                break
    if low > high[2] and low - high[2] >= atr * fvgMinAtr and bullishMove[1]
        bullFvg.updateZone(high[2], low)
    if high < low[2] and low[2] - high >= atr * fvgMinAtr and bearishMove[1]
        bearFvg.updateZone(high, low[2])

type SessionState
    int key = na
    float hi = na
    float lo = na
    int covered = 0
    int nextTime = na
    bool complete = false
    bool ready = false
    bool used = false
    int phase = 0
    int dir = 0
    int breakBar = na
    float impulse = na
    float origin = na
    float pullLow = na
    float pullHigh = na
    int pullBar = na
    int matches = 0
    string evidence = ""
    string status = "Waiting"

f_bounds(string spec, string zone) =>
    int sh = int(str.tonumber(str.substring(spec, 0, 2)))
    int sm = int(str.tonumber(str.substring(spec, 2, 4)))
    int eh = int(str.tonumber(str.substring(spec, 5, 7)))
    int em = int(str.tonumber(str.substring(spec, 7, 9)))
    int today = timestamp(zone, year(time, zone), month(time, zone), dayofmonth(time, zone), sh, sm)
    int start = time < today ? timestamp(zone, year(time, zone), month(time, zone), dayofmonth(time, zone) - 1, sh, sm) : today
    int finish = timestamp(zone, year(start, zone), month(start, zone), dayofmonth(start, zone) + (eh * 60 + em <= sh * 60 + sm ? 1 : 0), eh, em)
    bool workday = not weekdaysOnly or (dayofweek(start, zone) >= dayofweek.monday and dayofweek(start, zone) <= dayofweek.friday)
    [start, finish, workday and time >= start and time < finish]

method reset(SessionState s, int start) =>
    s.key := start
    s.hi := na
    s.lo := na
    s.covered := 0
    s.nextTime := na
    s.complete := false
    s.ready := false
    s.used := false
    s.phase := 0
    s.dir := 0
    s.status := "Waiting for ORB"

f_directionPass(int d) =>
    (d == 1 ? allowedDirection != "Short only" : allowedDirection != "Long only") and (trendMode == "None" or (d == 1 ? htfClose > htfEma : htfClose < htfEma))

// Returns an immutable signal-close estimate. The strategy models next-bar fills.
method step(SessionState s, string spec, string zone, bool enabled) =>
    [start, finish, active] = f_bounds(spec, zone)
    int orbStart = start + orbOffset * 60000
    int orbEnd = orbStart + orbMinutes * 60000
    int cutoff = finish - lastEntryBuffer * 60000
    int signal = 0
    float stop = na
    float target = na
    if barstate.isconfirmed
        if na(s.key) or s.key != start
            s.reset(start)
        if enabled and active
            bool windowOk = orbEnd < cutoff and orbOffset * 60 % chartSeconds == 0
            if not windowOk
                s.status := "ORB / cutoff conflict"
            else
                if time >= orbStart and time < orbEnd
                    if time == orbStart
                        s.complete := true
                        s.nextTime := time
                    s.complete := s.complete and time == s.nextTime and time_close <= orbEnd
                    s.covered += time_close - time
                    s.nextTime := time_close
                    s.hi := na(s.hi) ? high : math.max(s.hi, high)
                    s.lo := na(s.lo) ? low : math.min(s.lo, low)
                    s.status := "Building ORB"
                if time_close >= orbEnd and not s.ready
                    s.ready := s.complete and s.covered == orbMinutes * 60000 and s.nextTime == orbEnd
                    s.status := s.ready ? "Waiting for break" : "Incomplete / unaligned ORB"
                bool eligible = configOk and inDates and s.ready and not s.used and time >= orbEnd and (not delayWholeSetup or time >= start + delayMinutes * 60000) and time_close <= cutoff and not na(atr)
                float width = s.hi - s.lo
                bool rangeOk = width >= atr * minOrbAtr and width <= atr * maxOrbAtr
                // Invalidate even while an ATR-width filter temporarily blocks entries.
                // Otherwise a failed setup could revive when volatility changes again.
                bool invalid = s.phase > 0 and s.phase < 3 and (bar_index - s.breakBar > maxSetupBars or (s.dir == 1 ? close < s.lo : close > s.hi) or (s.phase == 2 and (s.dir == 1 ? close < s.pullLow : close > s.pullHigh)))
                if invalid
                    s.phase := 0
                    s.dir := 0
                    s.status := "Invalid / expired; wait for fresh break"
                if eligible and rangeOk
                    float buffer = math.max(syminfo.mintick, atr * breakAtr)
                    float tolerance = width * retestPercent / 100.0
                    // An invalidated setup cannot retest or confirm on the same bar.
                    if not invalid
                        int candidate = 0
                        bool delayReady = time_close >= start + delayMinutes * 60000
                        if s.phase == 0
                            int d = close > s.hi + buffer and close[1] <= s.hi + buffer and bullishMove ? 1 : close < s.lo - buffer and close[1] >= s.lo - buffer and bearishMove ? -1 : 0
                            if d != 0 and f_directionPass(d)
                                s.dir := d
                                s.phase := 1
                                s.breakBar := bar_index
                                s.impulse := d == 1 ? high : low
                                s.origin := d == 1 ? s.lo : s.hi
                                s.status := "Break confirmed; wait for retest"
                                if closeEntry
                                    // Never turn an early/filtered breakout into a delayed
                                    // stale-close entry or a hidden retest setup.
                                    s.phase := 0
                                    bool obTouch = d == 1 ? bullOb.overlaps(d) : bearOb.overlaps(d)
                                    bool fvgTouch = d == 1 ? bullFvg.overlaps(d) : bearFvg.overlaps(d)
                                    s.matches := (useOb and obTouch ? 1 : 0) + (useFvg and fvgTouch ? 1 : 0)
                                    s.evidence := (useOb and obTouch ? "OB " : "") + (useFvg and fvgTouch ? "FVG " : "")
                                    s.pullLow := low
                                    s.pullHigh := high
                                    if delayReady and (not requireContext or s.matches >= minContext)
                                        candidate := d
                        else if s.phase == 1 and bar_index > s.breakBar
                            int d = s.dir
                            float edge = d == 1 ? s.hi : s.lo
                            bool retest = d == 1 ? low <= edge + syminfo.mintick and low >= edge - tolerance and close > edge and close > open : high >= edge - syminfo.mintick and high <= edge + tolerance and close < edge and close < open
                            float leg = math.abs(s.impulse - s.origin)
                            float fibA = d == 1 ? s.impulse - leg * fibDeep : s.impulse + leg * fibShallow
                            float fibB = d == 1 ? s.impulse - leg * fibShallow : s.impulse + leg * fibDeep
                            bool fibTouch = low <= fibB and high >= fibA
                            bool obTouch = d == 1 ? bullOb.overlaps(d) : bearOb.overlaps(d)
                            bool fvgTouch = d == 1 ? bullFvg.overlaps(d) : bearFvg.overlaps(d)
                            int matches = (useOb and obTouch ? 1 : 0) + (useFvg and fvgTouch ? 1 : 0) + (useFib and fibTouch ? 1 : 0)
                            if retest and (not requireContext or matches >= minContext)
                                s.pullBar := bar_index
                                s.pullLow := low
                                s.pullHigh := high
                                s.matches := matches
                                s.evidence := (useOb and obTouch ? "OB " : "") + (useFvg and fvgTouch ? "FVG " : "") + (useFib and fibTouch ? "Fib " : "")
                                if entryModel == "Break + retest"
                                    // Before the delay, remain in phase 1. Require another
                                    // qualifying retest at/after the wait; do not queue it.
                                    if delayReady and f_directionPass(d)
                                        candidate := d
                                else
                                    s.phase := 2
                                    s.status := "Retest confirmed; wait for continuation"
                        else if s.phase == 2 and bar_index > s.pullBar
                            int d = s.dir
                            bool failedPullback = d == 1 ? close < s.pullLow : close > s.pullHigh
                            bool continuation = d == 1 ? close > math.max(s.impulse, s.pullHigh) + buffer and close > open : close < math.min(s.impulse, s.pullLow) - buffer and close < open
                            if failedPullback
                                s.phase := 0
                                s.dir := 0
                                s.status := "Pullback failed; wait for fresh break"
                            else if continuation and f_directionPass(d) and delayReady
                                candidate := d
                        // One common risk/target/quota path for all three entry modes.
                        if candidate != 0 and delayReady and f_directionPass(candidate)
                            int d = candidate
                            float anchor = stopModel == "Opposite ORB" ? (d == 1 ? s.lo : s.hi) : (d == 1 ? s.pullLow : s.pullHigh)
                            float rawStop = anchor - d * math.max(syminfo.mintick, atr * stopBufferAtr)
                            stop := d == 1 ? math.floor(rawStop / syminfo.mintick) * syminfo.mintick : math.ceil(rawStop / syminfo.mintick) * syminfo.mintick
                            float distance = d * (close - stop)
                            if distance >= math.max(syminfo.mintick, atr * minStopAtr) and distance <= atr * maxStopAtr
                                signal := d
                                target := math.round_to_mintick(close + d * distance * rewardRisk)
                                s.used := true
                                s.phase := 3
                                s.status := "Signal issued (daily quota used)"
                            else
                                s.phase := 0
                                s.dir := 0
                                s.status := "Stop distance rejected"
                if s.used
                    s.status := "Signal issued (daily quota used)"
                else if s.ready and time < start + delayMinutes * 60000
                    s.status := "Waiting for entry delay"
                else if time_close > cutoff
                    s.status := "Entry window closed"
                else if s.ready and time >= orbEnd and not invalid
                    s.status := not rangeOk ? "ORB width filtered" : s.phase == 0 ? "Waiting for fresh break" : s.phase == 1 ? "Waiting for retest" : "Waiting for continuation"
        else
            s.status := enabled ? "Outside session" : "Disabled"
    [signal, stop, target, active]

var SessionState asia = SessionState.new()
var SessionState london = SessionState.new()
var SessionState ny = SessionState.new()
bool scanAsia = asiaEnabled and (sessionMode == "All enabled sessions" or profileSession == "Asian")
bool scanLondon = londonEnabled and (sessionMode == "All enabled sessions" or profileSession == "London")
bool scanNy = nyEnabled and (sessionMode == "All enabled sessions" or profileSession == "New York")
[aSignal, aStop, aTarget, aActive] = asia.step(asiaSpec, asiaZone, scanAsia)
[lSignal, lStop, lTarget, lActive] = london.step(londonSpec, londonZone, scanLondon)
[nSignal, nStop, nTarget, nActive] = ny.step(nySpec, nyZone, scanNy)
array<int> signals = array.from(aSignal, lSignal, nSignal)
array<float> stops = array.from(aStop, lStop, nStop)
array<float> targets = array.from(aTarget, lTarget, nTarget)
array<string> names = array.from("Asian", "London", "New York")
array<int> matches = array.from(asia.matches, london.matches, ny.matches)
array<string> evidence = array.from(asia.evidence, london.evidence, ny.evidence)

f_quantity(float equity, float entry, float stop) =>
    float pointZar = syminfo.pointvalue * quoteToZar
    float riskUnit = (math.abs(entry - stop) + sizingCostTicks * syminfo.mintick) * pointZar
    float unitNotional = math.abs(entry) * pointZar
    float step = math.max(syminfo.mincontract, brokerStep)
    float riskQty = riskUnit > 0 ? math.max(equity, 0) * riskPercent / 100 / riskUnit : na
    float capQty = unitNotional > 0 ? math.max(equity, 0) * leverageCap * marginUsage / 100 / unitNotional : na
    not na(riskQty) and not na(capQty) and step > 0 ? math.floor(math.min(riskQty, capQty) / step) * step : na

f_price(float p) =>
    str.tostring(p, format.mintick)
f_message(string name, int d, float stop, float target, float qty, int count) =>
    (d == 1 ? "BUY" : "SELL") + " | " + syminfo.tickerid + " | TF " + timeframe.period + " | " + name + " | " + str.format_time(time_close, "yyyy-MM-dd HH:mm", "Africa/Johannesburg") + " SAST | EST entry " + f_price(close) + " SL " + f_price(stop) + " TP " + f_price(target) + " | R " + str.tostring(rewardRisk) + " | Qty " + str.tostring(qty) + (unitsPerLot > 0 ? " Lots " + str.tostring(qty / unitsPerLot, "#.####") : "") + " | Entry " + entryModel + " | Context " + contextMode + " " + str.tostring(count) + "/" + str.tostring(enabledContexts) + " | Manual decision; not an order"

plot(showRanges and scanAsia and aActive ? asia.hi : na, "Asian ORB high", color.new(asiaOrbColor, orbLineTransparency), linewidth = orbLineWidth, style = plot.style_linebr)
plot(showRanges and scanAsia and aActive ? asia.lo : na, "Asian ORB low", color.new(asiaOrbColor, orbLineTransparency), linewidth = orbLineWidth, style = plot.style_linebr)
plot(showRanges and scanLondon and lActive ? london.hi : na, "London ORB high", color.new(londonOrbColor, orbLineTransparency), linewidth = orbLineWidth, style = plot.style_linebr)
plot(showRanges and scanLondon and lActive ? london.lo : na, "London ORB low", color.new(londonOrbColor, orbLineTransparency), linewidth = orbLineWidth, style = plot.style_linebr)
plot(showRanges and scanNy and nActive ? ny.hi : na, "NY ORB high", color.new(nyOrbColor, orbLineTransparency), linewidth = orbLineWidth, style = plot.style_linebr)
plot(showRanges and scanNy and nActive ? ny.lo : na, "NY ORB low", color.new(nyOrbColor, orbLineTransparency), linewidth = orbLineWidth, style = plot.style_linebr)
bool buySignal = aSignal == 1 or lSignal == 1 or nSignal == 1
bool sellSignal = aSignal == -1 or lSignal == -1 or nSignal == -1
plotshape(buySignal, "Qualified BUY", shape.triangleup, location.belowbar, buySignalColor, text = "BUY", textcolor = buySignalColor, size = size.tiny)
plotshape(sellSignal, "Qualified SELL", shape.triangledown, location.abovebar, sellSignalColor, text = "SELL", textcolor = sellSignalColor, size = size.tiny)

int signalDirection = buySignal ? 1 : sellSignal ? -1 : 0
[m5FlowDir, m5FlowTime] = request.security(syminfo.tickerid, "5", [ta.valuewhen(signalDirection != 0, signalDirection, 0), ta.valuewhen(signalDirection != 0, time_close, 0)], gaps = barmerge.gaps_off, lookahead = barmerge.lookahead_off)
[m15FlowDir, m15FlowTime] = request.security(syminfo.tickerid, "15", [ta.valuewhen(signalDirection != 0, signalDirection, 0), ta.valuewhen(signalDirection != 0, time_close, 0)], gaps = barmerge.gaps_off, lookahead = barmerge.lookahead_off)
[m30FlowDir, m30FlowTime] = request.security(syminfo.tickerid, "30", [ta.valuewhen(signalDirection != 0, signalDirection, 0), ta.valuewhen(signalDirection != 0, time_close, 0)], gaps = barmerge.gaps_off, lookahead = barmerge.lookahead_off)
f_dayKey(int stamp) =>
    na(stamp) ? na : year(stamp, "Africa/Johannesburg") * 10000 + month(stamp, "Africa/Johannesburg") * 100 + dayofmonth(stamp, "Africa/Johannesburg")
f_flowText(int dir, int stamp) =>
    f_dayKey(stamp) != f_dayKey(time) ? "—" : dir == 1 ? "BUY" : dir == -1 ? "SELL" : "—"
string signalFlow = "M5 " + f_flowText(m5FlowDir, m5FlowTime) + " · M15 " + f_flowText(m15FlowDir, m15FlowTime) + " · M30 " + f_flowText(m30FlowDir, m30FlowTime)

var table panel = table.new(position.top_right, 2, 6, border_width = 1)
if showPanel and barstate.islast
    color bg = color.new(color.black, 12)
    string status = not chart.is_standard ? "Use standard OHLC candles" : not tfOk ? "Set aligned chart TF (profile " + requiredTf + "m)" : not contextOk ? (closeEntry ? "Close breakout: OB/FVG only; reduce matches" : "Fix context / Fib inputs") : not trendOk ? "Trend TF must exceed chart TF" : not configOk ? "Fix range / stop / date bounds" : "Confirmed-bar estimates"
    table.cell(panel, 0, 0, "ORB + context | research", text_color = color.white, bgcolor = bg)
    table.cell(panel, 1, 0, status, text_color = configOk ? color.teal : color.orange, bgcolor = bg)
    table.cell(panel, 0, 1, "Signal Flow", text_color = color.white, bgcolor = bg)
    table.cell(panel, 1, 1, signalFlow, text_color = color.white, bgcolor = bg)
    table.cell(panel, 0, 2, "Asian", text_color = color.white, bgcolor = bg)
    table.cell(panel, 1, 2, asia.status, text_color = color.white, bgcolor = bg)
    table.cell(panel, 0, 3, "London", text_color = color.white, bgcolor = bg)
    table.cell(panel, 1, 3, london.status, text_color = color.white, bgcolor = bg)
    table.cell(panel, 0, 4, "New York", text_color = color.white, bgcolor = bg)
    table.cell(panel, 1, 4, ny.status, text_color = color.white, bgcolor = bg)
