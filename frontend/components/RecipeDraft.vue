<script setup lang="ts">
import type { RecipeDraft } from '~/types/api'
const props = defineProps<{ recipe: RecipeDraft }>()
const targetServings = ref(props.recipe.servings)
const emit = defineEmits<{ publish: [withImage: boolean] }>()
const factor = computed(() => targetServings.value / props.recipe.servings)
function quantity(amount: number | null, scalable: boolean): string { if (amount === null) return ''; return new Intl.NumberFormat('de-DE', { maximumFractionDigits: 2 }).format(scalable ? amount * factor.value : amount) }
</script>
<template>
  <section class="card recipe"><header><div><span>{{ recipe.tags.join(' · ') }}</span><h2>{{ recipe.name }}</h2><p>{{ recipe.description }}</p></div><button @click="emit('publish', true)">In Mealie speichern</button></header><div class="meta"><label>Anzeige für <input v-model.number="targetServings" type="number" min="1" max="100"> Personen</label><span>{{ recipe.prep_minutes + recipe.cook_minutes }} Minuten</span></div><div class="columns"><div><h3>Zutaten</h3><ul><li v-for="item in recipe.ingredients" :key="item.name"><b>{{ quantity(item.amount, item.scalable) }} {{ item.unit }}</b> {{ item.name }}<template v-if="item.note">, {{ item.note }}</template><em v-if="!item.scalable"> nicht skalierbar</em></li></ul></div><div><h3>Zubereitung</h3><ol><li v-for="step in recipe.instructions" :key="step">{{ step }}</li></ol></div></div></section>
</template>
<style scoped>.card{background:#fff;border:1px solid #e1e7ef;border-radius:20px;padding:1.5rem;box-shadow:0 16px 40px #18253d0a}.recipe header,.meta{display:flex;justify-content:space-between;gap:1rem}.recipe header span{font-size:.75rem;font-weight:800;letter-spacing:.1em;color:#db661c;text-transform:uppercase}.recipe h2{margin:.35rem 0;font-size:2rem;letter-spacing:-.04em}.recipe p{color:#576575}.recipe button{background:#e96619;color:#fff;border:0;border-radius:10px;padding:.75rem 1rem;font-weight:750;align-self:flex-start}.meta{border-block:1px solid #e8edf3;padding:1rem 0;margin-top:1rem;align-items:center}.meta label{font-weight:700}.meta input{width:4.5rem;padding:.35rem;border:1px solid #c8d2df;border-radius:7px}.columns{display:grid;grid-template-columns:1fr 1fr;gap:2.5rem}.columns h3{font-size:.85rem;letter-spacing:.08em;text-transform:uppercase}.columns li{margin:.65rem 0;line-height:1.45}.columns em{font-size:.75rem;color:#637083}@media(max-width:650px){.recipe header,.meta{flex-direction:column}.columns{grid-template-columns:1fr}}</style>

