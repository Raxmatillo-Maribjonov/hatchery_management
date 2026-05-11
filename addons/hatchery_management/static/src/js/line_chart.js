/** @odoo-module **/
import { Component, xml } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";

const W = 1280, H = 340;
const PAD = { top: 26, right: 36, bottom: 58, left: 58 };
const CW = W - PAD.left - PAD.right;
const CH = H - PAD.top - PAD.bottom;

function fmtNum(n) {
    return n >= 1000 ? (n / 1000).toFixed(1) + "k" : String(n || 0);
}

function polyline(pts) {
    return pts.map((p, i) => (i === 0 ? `M${p.x},${p.y}` : `L${p.x},${p.y}`)).join(" ");
}

export class HatcheryLineChart extends Component {
    static template = xml`
<div class="hatchery_chart_wrapper">
  <t t-if="chartData and chartData.labels and chartData.labels.length">
    <!-- Legend -->
    <div class="hatchery_chart_legend">
      <t t-foreach="chartData.datasets" t-as="ds" t-key="ds.label">
        <span class="hatchery_legend_item">
          <span class="hatchery_legend_dot" t-att-style="'background:' + ds.color"/>
          <t t-esc="ds.label"/>
        </span>
      </t>
    </div>
    <!-- SVG -->
    <svg t-att-viewBox="'0 0 ' + W + ' ' + H" class="hatchery_chart_svg">
      <defs>
        <t t-foreach="chartData.datasets" t-as="ds" t-key="ds.label">
          <linearGradient t-att-id="'g_' + ds_index" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" t-att-stop-color="ds.color" stop-opacity="0.15"/>
            <stop offset="100%" t-att-stop-color="ds.color" stop-opacity="0"/>
          </linearGradient>
        </t>
      </defs>
      <!-- Grid -->
      <t t-foreach="yLines" t-as="yl" t-key="yl.y">
        <line t-att-x1="PAD.left" t-att-x2="PAD.left + CW"
              t-att-y1="yl.y" t-att-y2="yl.y" stroke="#f1f5f9" stroke-width="1"/>
        <text t-att-x="PAD.left - 6" t-att-y="yl.y + 4"
              text-anchor="end" fill="#94a3b8" font-size="10" t-esc="yl.lbl"/>
      </t>
      <!-- X axis -->
      <line t-att-x1="PAD.left" t-att-x2="PAD.left + CW"
            t-att-y1="PAD.top + CH" t-att-y2="PAD.top + CH"
            stroke="#e2e8f0" stroke-width="1"/>
      <!-- Lines per dataset -->
      <t t-foreach="svgDatasets" t-as="sds" t-key="sds.label">
        <path t-att-d="sds.area" t-att-fill="'url(#g_' + sds_index + ')'" stroke="none"/>
        <path t-att-d="sds.line" fill="none" t-att-stroke="sds.color"
              stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        <t t-foreach="sds.pts" t-as="pt" t-key="pt_index">
          <circle t-att-cx="pt.x" t-att-cy="pt.y" r="3.5"
                  fill="white" t-att-stroke="sds.color" stroke-width="2"/>
        </t>
      </t>
      <!-- X labels -->
      <t t-foreach="xLabels" t-as="xl" t-key="xl_index">
        <text t-att-x="xl.x" t-att-y="PAD.top + CH + 16"
              text-anchor="middle" fill="#64748b" font-size="10" t-esc="xl.lbl"/>
      </t>
    </svg>
  </t>
  <t t-else="">
    <div class="hatchery_chart_empty">Ma'lumot yo'q</div>
  </t>
</div>`;

    static props = { ...standardFieldProps };

    get W() { return W; }
    get H() { return H; }
    get PAD() { return PAD; }
    get CW() { return CW; }
    get CH() { return CH; }

    get chartData() {
        try {
            const raw = this.props.record.data[this.props.name];
            return raw ? JSON.parse(raw) : null;
        } catch { return null; }
    }

    get allValues() {
        const d = this.chartData;
        if (!d) return [0];
        return d.datasets.flatMap(ds => ds.data).filter(v => v > 0);
    }

    get maxVal() { return Math.max(...this.allValues, 1); }
    get n() { return (this.chartData?.labels || []).length; }

    _x(i) { return PAD.left + (this.n > 1 ? i * CW / (this.n - 1) : CW / 2); }
    _y(v) { return PAD.top + CH - (v / this.maxVal) * CH; }

    get yLines() {
        return [0, 0.25, 0.5, 0.75, 1].map(f => ({
            y: PAD.top + CH * (1 - f),
            lbl: fmtNum(Math.round(this.maxVal * f))
        }));
    }

    get svgDatasets() {
        const d = this.chartData;
        if (!d) return [];
        return d.datasets.map((ds, di) => {
            const pts = ds.data.map((v, i) => ({ x: this._x(i), y: this._y(v) }));
            const line = polyline(pts);
            const area = pts.length
                ? `M${pts[0].x},${PAD.top + CH} ` + polyline(pts).slice(1) + ` L${pts[pts.length-1].x},${PAD.top+CH} Z`
                : '';
            return { label: ds.label, color: ds.color, pts, line, area };
        });
    }

    get xLabels() {
        const d = this.chartData;
        if (!d) return [];
        return d.labels.map((lbl, i) => ({ x: this._x(i), lbl: (lbl || '').slice(0, 10) }));
    }
}

registry.category("fields").add("hatchery_line_chart", {
    component: HatcheryLineChart,
    supportedTypes: ["char"],
});
