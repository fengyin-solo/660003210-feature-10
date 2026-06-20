<template>
  <div class="bg-slate-800 rounded-lg p-4 border border-slate-700">
    <h3 class="text-sm font-bold text-slate-400 mb-3">ADMET 性质预测</h3>
    <div v-if="store.admet" class="space-y-4">
      <div
        class="rounded-lg p-4 border-2"
        :class="riskCardClasses"
      >
        <div class="flex items-center justify-between">
          <div>
            <div class="text-xs font-medium mb-1 opacity-80">综合风险评级</div>
            <div class="flex items-baseline gap-3">
              <span class="text-5xl font-black leading-none">{{ store.admet.riskLevel }}</span>
              <div>
                <div class="text-2xl font-bold">{{ store.admet.riskScore }}<span class="text-sm font-normal opacity-70"> / 14</span></div>
                <div class="text-xs mt-0.5 opacity-80">{{ riskLevelText }}</div>
              </div>
            </div>
          </div>
        </div>
        <div class="mt-4">
          <div class="h-3 bg-slate-900/50 rounded-full overflow-hidden">
            <div
              class="h-full rounded-full transition-all duration-500"
              :class="progressBarClasses"
              :style="{ width: (store.admet.riskScore / 14 * 100) + '%' }"
            ></div>
          </div>
          <div class="flex justify-between mt-1.5 text-[10px] opacity-60">
            <span>低风险 0</span>
            <span>4</span>
            <span>8</span>
            <span>12</span>
            <span>高风险 14</span>
          </div>
        </div>
      </div>

      <div v-if="store.admet.riskAlerts.length > 0" class="space-y-2">
        <div class="text-xs font-bold text-slate-400 flex items-center gap-1.5">
          <span>重点提示</span>
          <span class="bg-slate-700 px-1.5 py-0.5 rounded text-slate-300">{{ store.admet.riskAlerts.length }}</span>
        </div>
        <div
          v-for="(alert, idx) in store.admet.riskAlerts"
          :key="idx"
          class="rounded-lg p-3 flex gap-3 items-start"
          :class="alertTypeClasses(alert.type)"
        >
          <span class="text-xl flex-shrink-0 leading-none mt-0.5">
            {{ alert.type === 'danger' ? '⚠️' : alert.type === 'warning' ? '⚡' : 'ℹ️' }}
          </span>
          <div class="flex-1 min-w-0">
            <div class="font-bold text-sm">{{ alert.title }}</div>
            <div class="text-xs mt-1 opacity-90 leading-relaxed">{{ alert.detail }}</div>
          </div>
        </div>
      </div>

      <div class="grid grid-cols-2 gap-2 text-sm">
        <div class="bg-slate-900 rounded p-2">
          <div class="text-xs text-slate-500">LogP (脂溶性)</div>
          <div class="text-lg font-bold" :class="store.admet.logP > 3 ? 'text-red-400' : 'text-green-400'">{{ store.admet.logP }}</div>
        </div>
        <div class="bg-slate-900 rounded p-2">
          <div class="text-xs text-slate-500">LogS (溶解度)</div>
          <div class="text-lg font-bold text-cyan-400">{{ store.admet.logS }}</div>
        </div>
        <div class="bg-slate-900 rounded p-2">
          <div class="text-xs text-slate-500">蛋白结合率</div>
          <div class="text-lg font-bold text-purple-400">{{ store.admet.proteinBinding }}%</div>
        </div>
        <div class="bg-slate-900 rounded p-2">
          <div class="text-xs text-slate-500">生物利用度</div>
          <div class="text-lg font-bold" :class="store.admet.bioavailability > 50 ? 'text-green-400' : 'text-orange-400'">{{ store.admet.bioavailability }}%</div>
        </div>
      </div>
      <div class="bg-slate-900 rounded p-3 text-sm">
        <div class="flex justify-between mb-1"><span class="text-slate-500">毒性评估</span><span :class="store.admet.toxicity.includes('高') ? 'text-red-400' : store.admet.toxicity.includes('中') ? 'text-orange-400' : 'text-green-400'">{{ store.admet.toxicity }}</span></div>
        <div class="flex justify-between mb-1"><span class="text-slate-500">代谢稳定性</span><span :class="store.admet.metabolicStability === '稳定' ? 'text-green-400' : store.admet.metabolicStability === '中等' ? 'text-orange-400' : 'text-red-400'">{{ store.admet.metabolicStability }}</span></div>
        <div class="flex justify-between"><span class="text-slate-500">Lipinski五规则</span><span :class="store.admet.ruleOfFive ? 'text-green-400' : 'text-red-400'">{{ store.admet.ruleOfFive ? '✓ 通过' : '✗ 违反' }} ({{ store.admet.violations }})</span></div>
      </div>
    </div>
    <div v-else class="text-slate-500 text-sm">选择分子查看ADMET</div>

    <div v-if="store.similarMolecules.length > 0" class="mt-4">
      <h4 class="text-xs font-bold text-slate-500 mb-2">相似分子 (Tanimoto)</h4>
      <div class="space-y-1">
        <div v-for="mol in store.similarMolecules" :key="mol.id" @click="store.selectMolecule(mol)" class="cursor-pointer flex items-center justify-between bg-slate-900 rounded p-2 hover:bg-slate-700 transition">
          <span class="text-sm text-slate-200">{{ mol.name }}</span>
          <span class="text-xs font-bold" :style="{ color: mol.similarity > 60 ? '#22c55e' : mol.similarity > 30 ? '#eab308' : '#94a3b8' }">{{ mol.similarity }}%</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useMoleculeStore } from '../store/molecule'
const store = useMoleculeStore()

const riskCardClasses = computed(() => {
  if (!store.admet) return ''
  const level = store.admet.riskLevel
  if (level === 'A') return 'bg-green-900/30 border-green-500/60 text-green-200'
  if (level === 'B') return 'bg-blue-900/30 border-blue-500/60 text-blue-200'
  if (level === 'C') return 'bg-orange-900/30 border-orange-500/60 text-orange-200'
  return 'bg-red-900/30 border-red-500/60 text-red-200'
})

const progressBarClasses = computed(() => {
  if (!store.admet) return ''
  const level = store.admet.riskLevel
  if (level === 'A') return 'bg-gradient-to-r from-green-500 to-green-400'
  if (level === 'B') return 'bg-gradient-to-r from-blue-500 to-blue-400'
  if (level === 'C') return 'bg-gradient-to-r from-orange-500 to-orange-400'
  return 'bg-gradient-to-r from-red-500 to-red-400'
})

const riskLevelText = computed(() => {
  if (!store.admet) return ''
  const level = store.admet.riskLevel
  if (level === 'A') return '低风险 · 成药性优秀'
  if (level === 'B') return '较低风险 · 成药性良好'
  if (level === 'C') return '中等风险 · 需优化改进'
  return '高风险 · 成药性较差'
})

function alertTypeClasses(type: string) {
  if (type === 'danger') return 'bg-red-900/30 border border-red-500/40 text-red-100'
  if (type === 'warning') return 'bg-orange-900/30 border border-orange-500/40 text-orange-100'
  return 'bg-blue-900/30 border border-blue-500/40 text-blue-100'
}
</script>
