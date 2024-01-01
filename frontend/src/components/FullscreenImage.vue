<template>
    <div class="fixed inset-0 z-[100] bg-base-200 bg-opacity-80 flex justify-center items-center">
        <div class="w-[80%] h-[80%] bg-base-100 rounded-box p-5">
            <div class="flex justify-end">
                <button @click="closeFullscreen" class="btn btn-circle bg-base-200 drop-shadow-lg border-none backdrop-blur-md bg-opacity-80" tabindex="0">
                    <XMarkIcon class="h-5 w-auto" />
                </button>
            </div>
            <div class="flex justify-center">
                <img :src="imageurl" class="max-h-[80%] max-w-[80%] rounded-box" />
            </div>
            <div class="flex justify-center">
                <div class="flex flex-col items-center">
                    <h1 class="text-2xl font-bold">{{ title }}</h1>
                    <p class="text-sm">{{ explanation }}</p>
                </div>
            </div>
        </div>
    </div>
</template>



<script setup>
import { defineProps } from 'vue';
const props = defineProps(['imageurl', 'title', 'explanation'])

</script>