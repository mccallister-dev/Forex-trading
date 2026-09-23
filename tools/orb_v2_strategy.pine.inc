// Signal engine is identical to Manual v3. TradingView can hold only one net
// position here; concurrent manual signals are logged as skipped, not reversed.
// Relative tick brackets preserve modeled entry-to-target/stop distances after
// next-bar gaps. Their absolute prices may differ from the signal-close estimate.
var int skippedSignals = 0
var int submittedSignals = 0
var int positionLossTicks = na
var int positionProfitTicks = na
bool submittedThisBar = false
if barstate.isconfirmed
    for i = 0 to 2
        int d = array.get(signals, i)
        if d != 0
            float stop = array.get(stops, i)
            float qty = f_quantity(strategy.equity, close, stop)
            if strategy.position_size == 0 and not submittedThisBar and not na(qty) and qty > 0
                positionLossTicks := int(math.ceil(math.abs(close - stop) / syminfo.mintick))
                positionProfitTicks := int(math.round(positionLossTicks * rewardRisk))
                strategy.entry("ORB", d == 1 ? strategy.long : strategy.short, qty = qty, comment = array.get(names, i) + (d == 1 ? " BUY | " : " SELL | ") + entryModel)
                strategy.exit("SL/TP", "ORB", loss = positionLossTicks, profit = positionProfitTicks, comment_loss = "SL", comment_profit = "TP")
                submittedSignals += 1
                submittedThisBar := true
            else
                skippedSignals += 1
// No session/date flatten: open trades are allowed to finish at SL/TP.
float actualStop = strategy.position_size != 0 ? strategy.position_avg_price - math.sign(strategy.position_size) * positionLossTicks * syminfo.mintick : na
float actualTarget = strategy.position_size != 0 ? strategy.position_avg_price + math.sign(strategy.position_size) * positionProfitTicks * syminfo.mintick : na
plot(actualStop, "Tester actual SL", color.red, style = plot.style_linebr)
plot(actualTarget, "Tester actual TP", color.teal, style = plot.style_linebr)
if showPanel and barstate.islast
    table.cell(panel, 0, 8, "Tester submissions / skipped", text_color = color.white, bgcolor = color.new(color.black, 12))
    table.cell(panel, 1, 8, str.tostring(submittedSignals) + " / " + str.tostring(skippedSignals), text_color = color.white, bgcolor = color.new(color.black, 12))
