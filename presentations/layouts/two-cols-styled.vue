<script setup>
/**
 * Enhanced two-column layout with divider line and proper spacing.
 */
</script>

<template>
  <div class="two-cols-layout">
    <div class="cols-header">
      <slot name="default" />
    </div>
    <div class="cols-body">
      <div class="col col-left">
        <slot name="left" />
      </div>
      <div class="cols-divider" />
      <div class="col col-right">
        <slot name="right" />
      </div>
    </div>
  </div>
</template>

<style scoped>
.two-cols-layout {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #1A1A2E;
  padding: 48px 60px;
}

.cols-header {
  margin-bottom: 28px;
}

.cols-header :deep(h1) {
  font-family: 'DM Sans', sans-serif;
  font-weight: 700;
  font-size: 1.8em;
  color: #EAEAF0;
  letter-spacing: -0.02em;
}

.cols-body {
  flex: 1;
  display: flex;
  gap: 0;
  align-items: flex-start;
}

.col {
  flex: 1;
  padding: 0 24px;
}

.col-left {
  padding-left: 0;
}

.col-right {
  padding-right: 0;
}

.cols-divider {
  width: 1px;
  align-self: stretch;
  background: linear-gradient(180deg, transparent, rgba(255,255,255,0.08), transparent);
}

.col :deep(h3) {
  font-family: 'DM Sans', sans-serif;
  font-weight: 600;
  color: #FF7A45;
  font-size: 1em;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  margin-bottom: 16px;
}

.col :deep(ul) {
  list-style: none;
  padding: 0;
}

.col :deep(ul li) {
  position: relative;
  padding-left: 1.2em;
  margin-bottom: 10px;
  color: #9B9BB4;
  font-size: 0.9em;
}

.col :deep(ul li::before) {
  content: '';
  position: absolute;
  left: 0;
  top: 0.55em;
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: #E85D26;
}
</style>
