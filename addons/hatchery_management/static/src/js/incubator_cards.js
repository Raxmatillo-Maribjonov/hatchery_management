/** @odoo-module **/
import { Component, xml } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";

export class HatcheryIncubatorCards extends Component {
    static template = xml`
<div class="hatch-cards-grid">
  <t t-foreach="incubators" t-as="inc" t-key="inc.name">
    <div t-att-class="'hatch-inc-card ' + (inc.is_broken ? 'is-broken' : inc.state === 'loaded' ? 'is-loaded' : 'is-empty')">
      <div class="hatch-inc-head">
        <div class="hatch-inc-name">
          <t t-esc="inc.name"/>
        </div>
        <div t-if="inc.is_broken" class="hatch-badge hatch-badge-broken">
          <span class="hatch-dot"/> Buzilgan
        </div>
        <div t-elif="inc.state === 'loaded'" class="hatch-badge hatch-badge-loaded">
          <span class="hatch-dot"/> Faol
        </div>
        <div t-else="" class="hatch-badge hatch-badge-empty">
          <span class="hatch-dot"/> Bo'sh
        </div>
      </div>

      <div class="hatch-inc-body">
        <div class="hatch-inc-row">
          <span class="hatch-inc-label">Sig'im</span>
          <span class="hatch-inc-value"><t t-esc="inc.capacity.toLocaleString()"/> ta</span>
        </div>
        <t t-if="inc.state === 'loaded'">
          <div class="hatch-inc-row">
            <span class="hatch-inc-label">Partiya</span>
            <span class="hatch-inc-value hatch-inc-link"><t t-esc="inc.delivery"/></span>
          </div>
          <div class="hatch-inc-row">
            <span class="hatch-inc-label">Kirish</span>
            <span class="hatch-inc-value"><t t-esc="(inc.entry || '').slice(0,16)"/></span>
          </div>
          <div class="hatch-inc-row hatch-inc-row-last">
            <span class="hatch-inc-label">Chiqish</span>
            <span class="hatch-inc-value hatch-inc-exit"><t t-esc="(inc.exit || '').slice(0,16)"/></span>
          </div>
        </t>
      </div>
    </div>
  </t>
</div>`;

    static props = { ...standardFieldProps };

    get incubators() {
        try {
            const raw = this.props.record.data[this.props.name];
            return raw ? JSON.parse(raw) : [];
        } catch { return []; }
    }
}

registry.category("fields").add("hatchery_incubator_cards", {
    component: HatcheryIncubatorCards,
    supportedTypes: ["char"],
});
