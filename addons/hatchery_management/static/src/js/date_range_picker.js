/** @odoo-module **/

import { Component, useState, useRef, onMounted, onWillUnmount, xml } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { DateTime } from "luxon";

const MS  = ["Yan","Fev","Mar","Apr","May","Iyn","Iyl","Avg","Sen","Okt","Noy","Dek"];
const ML  = ["Yanvar","Fevral","Mart","Aprel","May","Iyun","Iyul","Avgust","Sentabr","Oktabr","Noyabr","Dekabr"];
const WD  = ["Du","Se","Ch","Pa","Ju","Sh","Ya"];
const QO  = [
    { key:"today",      label:"Bugun" },
    { key:"yesterday",  label:"Kecha" },
    { key:"last7",      label:"Soʻnggi 7 kun" },
    { key:"last30",     label:"Soʻnggi 30 kun" },
    { key:"this_month", label:"Bu oy" },
    { key:"last_month", label:"Oʻtgan oy" },
    { key:"this_year",  label:"Bu yil" },
];

function toJS(v) {
    if (!v) return null;
    if (v instanceof Date) return v;
    if (typeof v === "string") return new Date(v);
    if (v && typeof v.toJSDate === "function") return v.toJSDate();
    return null;
}

function isoStr(d) {
    if (!d) return false;
    const y = d.getFullYear();
    const m = String(d.getMonth()+1).padStart(2,"0");
    const day = String(d.getDate()).padStart(2,"0");
    return `${y}-${m}-${day}`;
}

export class HatcheryDateRangePicker extends Component {
    static template = xml`
<div class="hdrp-wrapper" t-ref="root">
  <div class="hdrp-trigger" t-on-click="(e) => this.toggle(e)">
    <i class="fa fa-calendar hdrp-icon"/>
    <span class="hdrp-display" t-esc="this.displayText"/>
    <i t-if="this.state.startDate" class="fa fa-times hdrp-clear" t-on-click="(e) => this.clearDates(e)"/>
  </div>
  <div t-if="this.state.isOpen" class="hdrp-dropdown" t-on-click.stop="">
    <div class="hdrp-body">
      <div class="hdrp-quick">
        <t t-foreach="this.QO" t-as="opt" t-key="opt.key">
          <div t-att-class="'hdrp-quick-item' + (this.state.activeQuick === opt.key ? ' hdrp-quick-active' : '')"
               t-on-click="() => this.setQuick(opt.key)" t-esc="opt.label"/>
        </t>
      </div>
      <div class="hdrp-vsep"/>
      <div class="hdrp-cals">
        <div class="hdrp-cal">
          <div class="hdrp-cal-hdr">
            <button class="hdrp-nav" t-on-click="() => this.prevMonth()">&#8249;</button>
            <span class="hdrp-month-lbl" t-esc="this.monthLabel1"/>
            <span style="width:28px"/>
          </div>
          <div class="hdrp-wdays">
            <t t-foreach="this.WD" t-as="wd" t-key="wd"><div t-esc="wd"/></t>
          </div>
          <div class="hdrp-grid">
            <t t-foreach="this.days1" t-as="day" t-key="day.date.getTime()">
              <div t-att-class="this.dayClass(day)"
                   t-on-click="() => this.clickDay(day.date)"
                   t-on-mouseenter="() => this.hoverDay(day.date)"
                   t-esc="day.date.getDate()"/>
            </t>
          </div>
        </div>
        <div class="hdrp-calsep"/>
        <div class="hdrp-cal">
          <div class="hdrp-cal-hdr">
            <span style="width:28px"/>
            <span class="hdrp-month-lbl" t-esc="this.monthLabel2"/>
            <button class="hdrp-nav" t-on-click="() => this.nextMonth()">&#8250;</button>
          </div>
          <div class="hdrp-wdays">
            <t t-foreach="this.WD" t-as="wd" t-key="wd"><div t-esc="wd"/></t>
          </div>
          <div class="hdrp-grid">
            <t t-foreach="this.days2" t-as="day" t-key="day.date.getTime()">
              <div t-att-class="this.dayClass(day)"
                   t-on-click="() => this.clickDay(day.date)"
                   t-on-mouseenter="() => this.hoverDay(day.date)"
                   t-esc="day.date.getDate()"/>
            </t>
          </div>
        </div>
      </div>
    </div>
    <div class="hdrp-footer">
      <button class="hdrp-btn-cancel" t-on-click="() => this.cancel()">Bekor qilish</button>
      <button class="hdrp-btn-apply" t-on-click="() => this.apply()">Qoʻlash</button>
    </div>
  </div>
</div>`;

    static props = { ...standardFieldProps };

    setup() {
        this.QO = QO;
        this.WD = WD;

        const rec = this.props.record;
        const df  = toJS(rec.data.date_from);
        const dt  = toJS(rec.data.date_to);
        const t   = new Date();
        const base = df || new Date(t.getFullYear(), t.getMonth(), 1);

        this.state = useState({
            isOpen: false, startDate: df, endDate: dt,
            hoverDate: null, selecting: null, activeQuick: null,
            month1: new Date(base.getFullYear(), base.getMonth(), 1),
            month2: new Date(base.getFullYear(), base.getMonth()+1, 1),
        });

        this.ref = useRef("root");
        this._out = (e) => {
            if (this.ref.el && !this.ref.el.contains(e.target)) this.state.isOpen = false;
        };
        onMounted(() => document.addEventListener("mousedown", this._out));
        onWillUnmount(() => document.removeEventListener("mousedown", this._out));
    }

    get displayText() {
        const { startDate: s, endDate: e } = this.state;
        const f = (d) => d ? `${MS[d.getMonth()]} ${d.getDate()}` : "";
        if (!s) return "Sana tanlang...";
        if (!e) return f(s);
        return `${f(s)}  –  ${f(e)}`;
    }
    get monthLabel1() { const m = this.state.month1; return `${ML[m.getMonth()]}  ${m.getFullYear()}`; }
    get monthLabel2() { const m = this.state.month2; return `${ML[m.getMonth()]}  ${m.getFullYear()}`; }

    _calDays(m) {
        const y = m.getFullYear(), mo = m.getMonth();
        const first = (new Date(y,mo,1).getDay()+6)%7;
        const total = new Date(y,mo+1,0).getDate();
        const days = [];
        for (let i=first-1;i>=0;i--) days.push({date:new Date(y,mo,-i),cur:false});
        for (let i=1;i<=total;i++)    days.push({date:new Date(y,mo,i), cur:true});
        const rem = 42-days.length;
        for (let i=1;i<=rem;i++)      days.push({date:new Date(y,mo+1,i),cur:false});
        return days;
    }
    get days1() { return this._calDays(this.state.month1); }
    get days2() { return this._calDays(this.state.month2); }

    _same(a,b) { return a&&b && a.getFullYear()===b.getFullYear() && a.getMonth()===b.getMonth() && a.getDate()===b.getDate(); }
    _inRange(d) {
        const {startDate:s,endDate:e,hoverDate:h,selecting:sel} = this.state;
        const end = (sel==="end"&&h)?h:e;
        if (!s||!end) return false;
        const lo=s<=end?s:end, hi=s<=end?end:s;
        return d>lo&&d<hi;
    }
    dayClass(day) {
        const d=day.date, cls=["hdrp-day"];
        if (!day.cur) cls.push("hdrp-other");
        if (this._same(d,new Date())) cls.push("hdrp-today");
        if (this._same(d,this.state.startDate)) cls.push("hdrp-sel","hdrp-start");
        else if (this._same(d,this.state.endDate)) cls.push("hdrp-sel","hdrp-end");
        else if (this._inRange(d)) cls.push("hdrp-range");
        return cls.join(" ");
    }

    clickDay(date) {
        const {startDate:s,endDate:e} = this.state;
        if (!s||e) { this.state.startDate=date; this.state.endDate=null; this.state.selecting="end"; this.state.activeQuick=null; }
        else {
            if (date<s) { this.state.endDate=s; this.state.startDate=date; }
            else this.state.endDate=date;
            this.state.selecting=null; this.state.hoverDate=null; this.state.activeQuick=null;
        }
    }
    hoverDay(date) { if (this.state.selecting==="end") this.state.hoverDate=date; }
    prevMonth() { const m=this.state.month1; this.state.month1=new Date(m.getFullYear(),m.getMonth()-1,1); this.state.month2=new Date(m.getFullYear(),m.getMonth(),1); }
    nextMonth() { const m=this.state.month1; this.state.month1=new Date(m.getFullYear(),m.getMonth()+1,1); this.state.month2=new Date(m.getFullYear(),m.getMonth()+2,1); }

    setQuick(key) {
        const t=new Date(); t.setHours(0,0,0,0);
        const y=t.getFullYear(),mo=t.getMonth(),d=t.getDate();
        let s,e;
        if (key==="today")      { s=e=new Date(t); }
        else if (key==="yesterday")  { s=e=new Date(y,mo,d-1); }
        else if (key==="last7")      { s=new Date(y,mo,d-6); e=new Date(t); }
        else if (key==="last30")     { s=new Date(y,mo,d-29); e=new Date(t); }
        else if (key==="this_month") { s=new Date(y,mo,1); e=new Date(y,mo+1,0); }
        else if (key==="last_month") { s=new Date(y,mo-1,1); e=new Date(y,mo,0); }
        else if (key==="this_year")  { s=new Date(y,0,1); e=new Date(t); }
        this.state.startDate=s; this.state.endDate=e;
        this.state.month1=new Date(s.getFullYear(),s.getMonth(),1);
        this.state.month2=new Date(s.getFullYear(),s.getMonth()+1,1);
        this.state.selecting=null; this.state.hoverDate=null; this.state.activeQuick=key;
    }

    toggle(e) { e.stopPropagation(); this.state.isOpen=!this.state.isOpen; }
    cancel() { this.state.isOpen=false; }
    clearDates(e) { e.stopPropagation(); this.state.startDate=null; this.state.endDate=null; this.state.activeQuick=null; }

    async apply() {
        const {startDate:s,endDate:e} = this.state;
        if (!s) return;
        await this.props.record.update({
            date_from: DateTime.fromJSDate(s),
            date_to:   DateTime.fromJSDate(e || s),
        });
        this.state.isOpen=false;
    }
}

registry.category("fields").add("hatchery_date_range", {
    component: HatcheryDateRangePicker,
    supportedTypes: ["char"],
});
