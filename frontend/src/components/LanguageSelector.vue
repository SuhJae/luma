<template>
  <div class="fixed inset-x-0 top-0 p-5 flex justify-end">
    <details class="dropdown dropdown-bottom dropdown-end">
      <summary class="btn btn-circle bg-base-200 drop-shadow-lg border-none backdrop-blur-md bg-opacity-80" tabindex="0" role="button">
        <LanguageIcon class="h-5 w-5"/>
        <!-- <img class="h-4 w-auto hidden sm:block" alt="Flag" :src="`/src/assets/lang-icon/${lang}.svg`"> -->
      </summary>
      <ul tabindex="0"
          class="dropdown-content z-[1] menu p-2 shadow bg-base-200 rounded-box w-36 backdrop-blur-md bg-opacity-80">
        <li>
          <p @click="changeLanguage('ko')"><img class="h-4 w-auto" src="/src/assets/lang-icon/ko.svg" role="button"
                                                alt="Flag of South Korea">한국어</p>
        </li>
        <li>
          <p @click="changeLanguage('en')"><img class="h-4 w-auto" src="/src/assets/lang-icon/en.svg" role="button"
                                                alt="Flag of USA">English
          </p>
        </li>
        <li>
          <p @click="changeLanguage('ja')"><img class="h-4 w-auto" src="/src/assets/lang-icon/ja.svg" role="button"
                                                alt="Flag of Japan">日本語</p>
        </li>
        <li>
          <p @click="changeLanguage('zh')"><img class="h-4 w-auto" src="/src/assets/lang-icon/zh.svg" role="button"
                                                alt="Flag of China">中文</p>
        </li>
      </ul>
    </details>
  </div>
</template>

<script setup>
import {inject} from 'vue';
import {
  LanguageIcon,
} from '@heroicons/vue/24/solid'

const changeLanguage = inject('changeLanguage');
</script>
