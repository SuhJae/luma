<template>
  <nav class="fixed inset-x-0 bottom-0 pb-4 md:pb-8 flex justify-center px-2">
    <div
        class="flex min-w-fit max-w-screen rounded-full px-1 h-14 items-center bg-base-200 drop-shadow-lg backdrop-blur-md bg-opacity-80 bouncy-transition"
        :class="(isSearchExpanded) ? 'w-[35rem]' : 'w-1'">
      <!-- Search Suggestions -->
      <div
          class="dropdown dropdown-hover dropdown-end absolute bottom-full mb-2 min-w-fit max-w-screen bg-base-200 p-4 rounded-xl shadow-lg"
          v-show="searchSuggestions.length && isSearchExpanded">
        <div v-for="item in searchSuggestions" class="max-w-full" tabindex="0">
          <p class="text-sm overflow-hidden overflow-ellipsis whitespace-nowrap">
            {{ item }}
          </p>
        </div>
      </div>
      <button class="flex-none btn btn-ghost btn-circle p-0 m-0" v-show="!isSearchExpanded" @click="home();">
        <img src="../assets/logo.png" alt="Joseon Space" class="w-6 h-6">
      </button>
      <!-- Breadcrumb items -->
      <div class="flex-none w-5 h-5" v-show="!isSearchExpanded">
        <ChevronRightIcon/>
      </div>
      <div class="flex-1" v-show="!isSearchExpanded">
        <div class="flex-none dropdown dropdown-top">
          <div tabindex="0" role="button" class="btn btn-ghost rounded-full px-2">
            <p class="text-sm font-normal overflow-hidden whitespace-nowrap overflow-ellipsis max-w-[21vw] underline">
              {{ selectedPalace === '0' ? langData.selectpalace : palaceDict[selectedPalace] }}
            </p>
          </div>
          <div class="backdrop-blur-md bg-opacity-80 dropdown-content z-[1] menu p-2 shadow rounded-box w-52 max-h-[60vh] overflow-y-auto grid bg-base-200" tabindex="0">
            <li v-for="(item, key) in palaceDict" :key="key" class="max-w-52">
              <a @click=changePalace(key) :href="palaceURL[key] + '/'" @click.prevent>
                {{ item }}
              </a>
            </li>
          </div>
        </div>
      </div>
      <div class="flex-none w-5 h-5" v-show="!isSearchExpanded && selectedPalace !== '0'">
        <ChevronRightIcon/>
      </div>
      <div class="flex-1" v-show="!isSearchExpanded && selectedPalace !== '0'">
        <div class="flex-none dropdown dropdown-top dropdown-end">
          <div tabindex="0" role="button" class="btn btn-ghost rounded-full px-2">
            <p class="text-sm font-normal overflow-hidden whitespace-nowrap overflow-ellipsis max-w-[21vw] underline">
              {{ selectedBuilding === -1 ? langData.selectbuilding : buildingsArray[selectedBuilding].name }}
            </p>
          </div>
          <div class="backdrop-blur-md bg-opacity-80 dropdown-content z-[1] menu p-2 shadow rounded-box w-52 max-h-[60vh] overflow-y-auto grid bg-base-200" tabindex="0">
            <li v-for="(item, i) in buildingsArray" :key="i" class="max-w-52">
              <a @click="changeBuilding(i)" :href="palaceURL[selectedPalace] + '/' + item.url + '/'" @click.prevent>
                {{ item.name }}
              </a>
            </li>
          </div>
        </div>
      </div>
      <div class="flex-1 w-fit">
        <!-- Normal Search Button -->
        <button class="btn btn-ghost btn-circle px-3" v-show="!isSearchExpanded" @click="openSearch" aria-label="Open search">
          <MagnifyingGlassIcon class="w-6 h-6"/>
        </button>
        <!-- Expanded Search Input -->
        <div class="relative w-full" v-show="isSearchExpanded">
          <div class="flex items-center">
            <input class="bg-transparent pl-10 w-full border-none focus:outline-none" type="text"
                   autocomplete="off" @keydown.enter="commitSearch" :placeholder="langData.searchPlaceholder"
                   id="search" @input="searchPreview" :value="searchValue">
            <MagnifyingGlassIcon class="w-6 h-6 absolute left-2"/>
            <button class="btn btn-ghost btn-circle px-3" @click="closeSearch" aria-label="Close search">
              <XMarkIcon class="w-6 h-6"/>
            </button>
          </div>
        </div>
      </div>
    </div>
  </nav>
</template>


<style>
.bouncy-transition {
  transition: width 0.2s cubic-bezier(.44, .09, .37, .93);
}
</style>


<script setup>
import {ref, nextTick, inject, onMounted} from 'vue';
import {MagnifyingGlassIcon, ChevronRightIcon, XMarkIcon} from '@heroicons/vue/24/solid';

const lang = inject('lang');
const langData = inject('langData');
const palaceDict = inject('palaceDict');
const selectedBuilding = inject('selectedBuilding');
const selectedPalace = inject('selectedPalace');
const buildingSlug = inject('buildingSlug');
const buildingsArray = inject('buildingsArray');
const palaceURL = inject('palaceURL');

const isSearchExpanded = ref(false);
let searchSuggestions = ref([]);
let searchValue = ref('');

const changePalace = (palace) => {
  selectedPalace.value = palace;
  selectedBuilding.value = -1;
}

const changeBuilding = (building) => {
  selectedBuilding.value = building;
  buildingSlug.value = buildingsArray.value[building].url;
}

const home = () => {
  // When already on the home page, scroll to top
  if (selectedPalace.value === '0' && selectedBuilding.value === -1) {
    window.scrollTo({top: 0, behavior: 'smooth'});
    return;
  } else {
    selectedPalace.value = '0';
    selectedBuilding.value = -1;
  }
}

const openSearch = () => {
  isSearchExpanded.value = true;
  nextTick(() => {
    const searchInput = document.getElementById('search');
    if (searchInput) {
      searchInput.focus();
    }
  });
};

const closeSearch = () => {
  isSearchExpanded.value = false;
};

const searchPreview = (event) => {
  searchValue.value = event.target.value;
  if (searchValue.value.trim().length && searchValue.value.length < 50) {
    fetchAutocomplete();
  } else {
    searchSuggestions.value = [];
  }
}

const fetchAutocomplete = async () => {
  try {
    const response = await fetch(window.location.origin + "/api/v1/autocomplete/?keyword=" + searchValue.value + "&language=" + lang.value);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    searchSuggestions.value = data['suggestions'];
  } catch (error) {
    console.error("Error in fetchAutocomplete:", error);
  }
};

const commitSearch = () => {
  if (searchValue.value.trim().length) {
    window.history.pushState({}, '', '/search?keyword=' + searchValue.value);
    searchValue.value = '';
    searchSuggestions.value = [];
    selectedPalace.value = '0';
    selectedBuilding.value = -1;
    closeSearch();
  }
}

onMounted(() => {
  window.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') {
      isSearchExpanded.value = false;
    }
  });
});

</script>