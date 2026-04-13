<script setup>
/**
 * Styled comparison table with highlight support.
 *
 * Usage:
 *   <CompareTable
 *     :columns="['Feature', 'Us', 'Competitor A', 'Competitor B']"
 *     :rows="[
 *       ['Real-time sync', true, false, true],
 *       ['Price', '$10/mo', '$25/mo', '$15/mo'],
 *       ['Support', '24/7', 'Business hours', 'Email only'],
 *     ]"
 *     :highlight="1"
 *   />
 *
 *   Boolean values render as ✓ / ✗ with color coding.
 *   :highlight is the 0-based column index to emphasize (usually "our" column).
 */
defineProps({
  columns: { type: Array, required: true },
  rows: { type: Array, required: true },
  highlight: { type: Number, default: 1 },
})
</script>

<template>
  <div class="compare-wrap">
    <table class="compare-table">
      <thead>
        <tr>
          <th
            v-for="(col, ci) in columns"
            :key="ci"
            :class="{ highlighted: ci === highlight }"
          >
            {{ col }}
          </th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(row, ri) in rows" :key="ri">
          <td
            v-for="(cell, ci) in row"
            :key="ci"
            :class="{ highlighted: ci === highlight }"
          >
            <span v-if="cell === true" class="check">✓</span>
            <span v-else-if="cell === false" class="cross">✗</span>
            <span v-else>{{ cell }}</span>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<style scoped>
.compare-wrap {
  overflow-x: auto;
}
.compare-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  font-size: 0.85em;
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.08);
}
.compare-table th {
  font-family: 'DM Sans', sans-serif;
  font-weight: 600;
  padding: 14px 18px;
  background: #232340;
  color: #9B9BB4;
  text-align: center;
  font-size: 0.9em;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border-bottom: 2px solid rgba(255, 255, 255, 0.06);
}
.compare-table th:first-child {
  text-align: left;
}
.compare-table th.highlighted {
  color: #FF7A45;
  background: rgba(232, 93, 38, 0.1);
  border-bottom-color: #E85D26;
}
.compare-table td {
  padding: 12px 18px;
  text-align: center;
  color: #9B9BB4;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}
.compare-table td:first-child {
  text-align: left;
  color: #EAEAF0;
  font-weight: 500;
}
.compare-table td.highlighted {
  background: rgba(232, 93, 38, 0.04);
  color: #EAEAF0;
  font-weight: 500;
}
.compare-table tbody tr:last-child td {
  border-bottom: none;
}
.check {
  color: #34C77B;
  font-weight: 700;
  font-size: 1.1em;
}
.cross {
  color: #E74C5E;
  font-weight: 700;
  font-size: 1.1em;
}
</style>
