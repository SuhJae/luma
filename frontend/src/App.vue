<template>
  <teleport to="head">
    <!-- Search Schema -->
    <component :is="'script'" type="application/ld+json">
      {
      "@context": "https://schema.org",
      "@type": "WebSite",
      "url": "https://luma.joseon.space/",
      "potentialAction": {
      "@type": "SearchAction",
      "target": {
      "@type": "EntryPoint",
      "urlTemplate": "https://luma.joseon.space/search?keyword={search_term_string}"
      },
      "query-input": "required name=search_term_string"
      }
      }
    </component>

    <meta name="description" content="Find out more about the buildings of the Joseon Dynasty." v-if="buildingSlug === ''"/>

    <!-- Link tags to other pages -->
    <link rel="alternate" hreflang="ko" :href="`https://luma.joseon.space/${palaceURL[selectedPalace]}`"
          v-if="selectedPalace !== '0' && lang !== 'ko' && buildingSlug === ''"/>
    <link rel="alternate" hreflang="en" :href="`https://luma.joseon.space/${palaceURL[selectedPalace]}`"
          v-if="selectedPalace !== '0' && lang !== 'en' && buildingSlug === ''"/>
    <link rel="alternate" hreflang="ja" :href="`https://luma.joseon.space/${palaceURL[selectedPalace]}`"
          v-if="selectedPalace !== '0' && lang !== 'ja' && buildingSlug === ''"/>
    <link rel="alternate" hreflang="zh" :href="`https://luma.joseon.space/${palaceURL[selectedPalace]}`"
          v-if="selectedPalace !== '0' && lang !== 'zh' && buildingSlug === ''"/>
  </teleport>


  <LanguageSelector class="z-[1] lg:z-[3]"/>
  <Navigation class="z-[3]"/>
  <DetailModel :building="buildingSlug" v-if="showDetail" @close="handleDetilClose"/>

  <!-- Landing Page Intro  -->
  <div class="hero h-[50vh]">
    <div class="hero-content text-center">
      <div class="max-w-md">
        <h2 class="text-5xl font-bold mb-4"> {{
            selectedPalace === '0' ? langData.joseonSpace :
                palaceDict[selectedPalace]
          }} </h2>
        <p class="text-3xl font-semibold"> {{ langData.title }}
          <span class="mx-2 badge badge-lg badge-primary">
            Alpha
          </span>
        </p>
      </div>
    </div>
  </div>

  <!-- Building Feed -->
  <div class="flex justify-center items-center px-4">
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 max-w-screen-lg w-full">
      <div class="card h-80 overflow-hidden bg-base-100 shadow-xl rounded-lg w-full cursor-pointer"
           v-for="building in buildings" :key="building.id"
           @click="showBuildingDetail(building.url, building.palace_code)"
           @click.prevent>
        <div :class="{ 'skeleton': !building.imageLoaded }" class="w-full h-2/3">
          <img :src="'/api/v1/media/' + building.thumbnail" :alt="building.name" loading="lazy"
               class="w-full h-full object-cover" @load="building.imageLoaded = true">
        </div>
        <div class="absolute bottom-0 w-full p-4 bg-base-100/80 backdrop-blur-md">
          <h4 class="text-lg w-full font-semibold truncate">{{ building.name }}</h4>
          <div class="h-16">
            <p class="text-sm w-full ellipsis-multi-3">{{ building.explanation }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>

  <footer class="footer footer-center p-4 mt-12 bg-base-300 text-base-content pb-32">
    <aside>
      <p>Made with <span class="text-primary">♥</span> by <a href="https://twitter.com/_suhjae" target="_blank" class="link link-primary"
                           rel="noopener noreferrer">@_SuhJae</a></p>
    </aside>
  </footer>
</template>


<style>
.ellipsis-multi-3 {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}

.ellipsis-multi-6 {
  display: -webkit-box;
  -webkit-line-clamp: 6;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>


<script setup>
import LanguageSelector from './components/LanguageSelector.vue';
import Navigation from './components/Navigation.vue';
import DetailModel from './components/DetailModel.vue';

import {provide, ref, computed, watch, onMounted} from 'vue';
import {useLanguageStore} from './store/languageStore';
import {themeChange} from 'theme-change'

const {lang, langData, changeLanguage} = useLanguageStore();
const buildings = ref([]);
const showDetail = ref(false);
const buildingSlug = ref('');
const selectedPalace = ref('0');
const selectedBuilding = ref(-1);
const buildingsArray = ref([]);

const palaceDict = computed(() => ({
  '1': langData.gyeongbokgung,
  '2': langData.changdeokgung,
  '3': langData.changgyeonggung,
  '4': langData.deoksugung,
  '5': langData.jongmyo,
}));

const palaceURL = {
  '1': 'gyeongbokgung',
  '2': 'changdeokgung',
  '3': 'changgyeonggung',
  '4': 'deoksugung',
  '5': 'jongmyo',
}

const fetchRandom = async () => {
  try {
    const response = await fetch(window.location.origin + "/api/v1/random/?language=" + lang.value + "&palace_id=" + selectedPalace.value);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json(); // Correctly parsing JSON
    buildings.value = data;
  } catch (error) {
    console.error("Error in fetchRandom:", error);
  }
  updateTitle();
}


const showBuildingDetail = (Slug, palaceCode) => {
  console.log("Show Building Detail (Slug: " + Slug + ", Palace Code: " + palaceCode + ")");
  if (palaceCode !== selectedPalace.value) {
    selectedPalace.value = palaceCode;
  }
  buildingSlug.value = Slug;
}

const updateUrl = () => {
  let url = '/';
  if (selectedPalace.value !== '0') {
    url += palaceURL[selectedPalace.value];
    if (buildingSlug.value !== "") {
      url += '/' + buildingSlug.value;
    }
  }
  if (window.location.pathname !== url) {
    window.history.pushState({}, '', url);
  }
  updateTitle();
}

const handleDetilClose = () => {
  showDetail.value = false;
  buildingSlug.value = '';
  selectedBuilding.value = -1;
}

if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js')
        .then(registration => {
          console.log('ServiceWorker registration successful with scope: ', registration.scope);
        }, err => {
          console.log('ServiceWorker registration failed: ', err);
        });
  });
}

const fetchBuildings = async () => {
  if (selectedPalace.value === '0') {
    buildingsArray.value = [];
    return;
  }
  try {
    const response = await fetch(window.location.origin + '/api/v1/buildings?palace_id=' + selectedPalace.value + '&language=' + lang.value);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    buildingsArray.value = data;
    console.log("Buildings Array:", buildingsArray.value);
    selectedBuilding.value = buildingsArray.value.findIndex(item => item.url === buildingSlug.value);
  } catch (error) {
    console.error("Error in fetchBuildings:", error);
  }
};

const parseUrl = async (saveHistory = true) => {
  const url = window.location.pathname;
  console.log("Parsing URL: " + url);
  const urlArray = url.split('/').filter(item => item !== '');

  selectedPalace.value = Object.keys(palaceURL).find(key => palaceURL[key] === urlArray[0]) || '0';

  if (selectedPalace.value !== '0') {
    await fetchBuildings();
    if (urlArray.length === 2) {
      let index = buildingsArray.value.findIndex(item => item.url === urlArray[1]);
      selectedBuilding.value = index !== -1 ? index : -1;
      buildingSlug.value = index !== -1 ? urlArray[1] : '';
      showDetail.value = index !== -1;
      document.body.style.overflow = showDetail.value ? 'hidden' : 'auto';
    }
  }
  // Update the URL without pushing a new state
  if (!saveHistory) {
    window.history.replaceState({}, '', url);
  }
  await fetchRandom();
}

const updateTitle = () => {
  if (buildingSlug.value === '') {
    if (selectedPalace.value === '0') {
      document.title = langData.joseonSpace + ' ' + langData.title;
    } else {
      document.title = palaceDict.value[selectedPalace.value] + ' - ' + langData.title;
    }
  }
}

watch(selectedPalace, () => {
  updateUrl();
  buildings.value = [];
  fetchRandom();
  showDetail.value = buildingSlug.value !== '';
  document.body.style.overflow = showDetail.value ? 'hidden' : 'auto';
})

watch(lang, () => {
  fetchRandom();
  fetchBuildings();
})

watch(buildingSlug, () => {
  updateUrl();
  showDetail.value = buildingSlug.value !== '';
  document.body.style.overflow = showDetail.value ? 'hidden' : 'auto';
  selectedBuilding.value = buildingsArray.value.findIndex(item => item.url === buildingSlug.value);
})

// watch user nevigating manually back and forth
window.addEventListener('popstate', () => {
  parseUrl(false);
});

watch([selectedPalace, lang], fetchBuildings, {immediate: true});

// ========== Theme Management ==========
const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
const isDarkTheme = ref(prefersDark);
watch(isDarkTheme, (newValue) => {
  console.log("Theme changed:", newValue);
  document.documentElement.setAttribute('data-theme', newValue ? 'theRealmOfTwilightSerenity' : 'theLandofMorningCalm');
});
window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', event => {
  isDarkTheme.value = event.matches;
});
document.documentElement.setAttribute('data-theme', prefersDark ? 'theRealmOfTwilightSerenity' : 'theLandofMorningCalm');

onMounted(() => {
  themeChange(true);
});

parseUrl();

provide('lang', lang);
provide('langData', langData);
provide('changeLanguage', changeLanguage);
provide('palaceDict', palaceDict);
provide('palaceURL', palaceURL);
provide('selectedPalace', selectedPalace);
provide('selectedBuilding', selectedBuilding);
provide('buildingSlug', buildingSlug);
provide('buildingsArray', buildingsArray);
</script>