// This companion contains NO strategy orders and connects to NO broker.
type Plan
    int dir
    int bornBar
    int bornDay
    float stop
    float target
    bool active
    line entryLine
    line stopLine
    line targetLine
    label caption
    string initialText

var array<Plan> plans = array.new<Plan>()
int sastDay = year(time, "Africa/Johannesburg") * 10000 + month(time, "Africa/Johannesburg") * 100 + dayofmonth(time, "Africa/Johannesburg")
var int daySequence = 0
if barstate.isconfirmed and (barstate.isfirst or sastDay != sastDay[1])
    daySequence += 1
var int omittedDrawings = 0
if barstate.isconfirmed
    if array.size(plans) > 0
        for i = array.size(plans) - 1 to 0
            Plan p = array.get(plans, i)
            if p.active and bar_index > p.bornBar
                line.set_x2(p.entryLine, time_close)
                line.set_x2(p.stopLine, time_close)
                line.set_x2(p.targetLine, time_close)
                bool slHit = p.dir == 1 ? low <= p.stop : high >= p.stop
                bool tpHit = p.dir == 1 ? high >= p.target : low <= p.target
                if slHit or tpHit
                    p.active := false
                    string result = slHit and tpHit ? "BOTH levels touched: ambiguous" : slHit ? "SL level touched" : "TP level touched"
                    label.set_text(p.caption, p.initialText + "\n" + result)
                    label.set_color(p.caption, slHit and tpHit ? color.gray : slHit ? color.new(color.red, 25) : color.new(color.teal, 25))
            if not p.active and daySequence - p.bornDay >= retainDays
                line.delete(p.entryLine)
                line.delete(p.stopLine)
                line.delete(p.targetLine)
                label.delete(p.caption)
                array.remove(plans, i)
    for i = 0 to 2
        int d = array.get(signals, i)
        if d != 0
            float stop = array.get(stops, i)
            float target = array.get(targets, i)
            float qty = f_quantity(manualEquity, close, stop)
            string message = f_message(array.get(names, i), d, stop, target, qty, array.get(matches, i)) + " | " + array.get(evidence, i)
            if enableAlerts
                alert(message, alert.freq_all)
            // All active plans persist. Resource ceiling suppresses new DRAWINGS only.
            // Signal markers and alerts remain available; no existing plan is deleted.
            if array.size(plans) < 140
                string labelText = (d == 1 ? "BUY" : "SELL") + " | " + array.get(names, i) + "\n" + entryModel + "\nEst E " + f_price(close) + "  SL " + f_price(stop) + "\nTP " + f_price(target) + " (" + str.tostring(rewardRisk) + "R)\nQty " + str.tostring(qty, "#.####") + (unitsPerLot > 0 ? " | lots " + str.tostring(qty / unitsPerLot, "#.####") : "") + "\nContext: " + (not requireContext ? "Off" : array.get(evidence, i))
                color c = d == 1 ? buySignalColor : sellSignalColor
                line el = line.new(time_close, close, time_close + int(chartSeconds * 1000), close, xloc = xloc.bar_time, color = color.gray, style = line.style_dotted)
                line sl = line.new(time_close, stop, time_close + int(chartSeconds * 1000), stop, xloc = xloc.bar_time, color = sellSignalColor)
                line tl = line.new(time_close, target, time_close + int(chartSeconds * 1000), target, xloc = xloc.bar_time, color = buySignalColor)
                label lab = label.new(time_close, d == 1 ? low : high, labelText, xloc = xloc.bar_time, style = d == 1 ? label.style_label_up : label.style_label_down, color = color.new(c, 20), textcolor = color.white, size = size.small)
                array.push(plans, Plan.new(d, bar_index, daySequence, stop, target, true, el, sl, tl, lab, labelText))
            else
                omittedDrawings += 1
if showPanel and barstate.islast
    int activePlans = 0
    for p in plans
        if p.active
            activePlans += 1
    table.cell(panel, 0, 5, "Manual plans (not positions)", text_color = color.white, bgcolor = color.new(color.black, 12))
    table.cell(panel, 1, 5, str.tostring(activePlans) + " active | omitted drawings " + str.tostring(omittedDrawings), text_color = color.white, bgcolor = color.new(color.black, 12))
alertcondition(buySignal, "Qualified BUY", "ORB qualified BUY. Use Any alert() function call for estimated levels.")
alertcondition(sellSignal, "Qualified SELL", "ORB qualified SELL. Use Any alert() function call for estimated levels.")
