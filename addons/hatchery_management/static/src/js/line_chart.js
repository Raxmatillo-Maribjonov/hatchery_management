/** @odoo-module **/

import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";

const W = 900, H = 240;
const PAD = { top: 20, right: 30, bottom: 36, left: 60 };
const CW = W - PAD.left - PAD.right;
const CH = H - PAD.top - PAD.bottom;

function fmtNum(n) {
    if (n >= 1000) return (n / 1000).toFixed(1) + "k";
    return String(n);
}

function smooth(pts) {
    if (pts.length < 2) return pts.map(p => `L${p.x},${p.y}`).join(" ");
    let d = "";
    for (let i = 1; i < pts.length; i++) {
        const cpx = (pts[i-1].x + pts[i].x) / 2;
        d += ` C${cpx},${pts[i-1].y} ${cpx},${pts[i].y} ${pts[i].x},${pts[i].y}`;
    }
    return d;
}

export class HatcheryLineChart extends Component {
    static template = "hatchery_management.HatcheryLineChart";
    static props = { ...standardFieldProps };

    get data() {
        try { return JSON.parse(this.props.record.data.chart_data || "{}"); }
        catch { return { labels: [], eggs: [], chicks: [], partiya: [] }; }
    }

    get svgData() {
        const d = this.data;
        if (!d.labels || d.labels.length < 2) return null;

        const n = d.labels.length;
        const allVals = [...(d.eggs || []), ...(d.chicks || [])];
        const maxVal  = Math.max(...allVals, 1);

        const xStep = CW / (n - 1);

        const pts = (arr) => arr.map((v, i) => ({
            x: PAD.left + i * xStep,
            y: PAD.top + CH - (v / maxVal) * CH,
        }));

        const eggsP   = pts(d.eggs || []);
        const chicksP = pts(d.chicks || []);

        const linePath = (p) => `M${p[0].x},${p[0].y}` + smooth(p);
        const areaPath = (p) => `M${p[0].x},${PAD.top + CH}` +
            ` L${p[0].x},${p[0].y}` + smooth(p) +
            ` L${p[p.length-1].x},${PAD.top + CH} Z`;

        // Y grid lines (5 lines)
        const yLines = Array.from({length: 5}, (_, i) => {
            const frac = i / 4;
            return {
                y: PAD.top + CH * (1 - frac),
                label: fmtNum(Math.round(maxVal * frac)),
            };
        });

        return {
            w: W, h: H,
            eggsLine:   linePath(eggsP),
            chicksLine: linePath(chicksP),
            eggsArea:   areaPath(eggsP),
            chicksArea: areaPath(chicksP),
            eggsPoints: eggsP.map((p, i) => ({ ...p, v: d.eggs[i] })),
            chicksPoints: chicksP.map((p, i) => ({ ...p, v: d.chicks[i] })),
            labels:  d.labels.map((l, i) => ({ label: l, x: PAD.left + i * xStep })),
            yLines,
            xLeft:  PAD.left,
            xRight: PAD.left + CW,
            yTop:   PAD.top,
            yBot:   PAD.top + CH,
            year:   d.year || new Date().getFullYear(),
        };
    }
}

registry.category("fields").add("hatchery_line_chart", {
    component: HatcheryLineChart,
    supportedTypes: ["char"],
});
