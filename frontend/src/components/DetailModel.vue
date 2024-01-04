<template>
  <Teleport to="head">
    <meta name="title" :content="buildingData.name + ' (' + palaceDict[selectedPalace] + ') - ' + langData.title">
    <meta name="description" :content="buildingData.explanation?.substring(0, 150)">
    <meta name="keywords" content="경복궁, 창덕궁, 창경궁, 덕수궁, 종묘, 한국문화, 문화재청, 문화재, 문화, 문화유산, 문화유적, 문화유적지, 투어, 관광정보">
    <meta name="robots" content="index, follow">
    <meta name="language" :content="lang">

    <!-- Open Graph / Facebook -->
    <meta property="og:type" content="website">
    <meta property="og:url" :content="'https://luma.joseon.space/api/v1/buildingurl/' + buildingData.url">
    <meta property="og:title"
          :content="buildingData.name + ' (' + palaceDict[selectedPalace] + ') - ' + langData.title">
    <meta property="og:description" :content="buildingData.explanation?.substring(0, 150)">
    <meta property="og:image" :content="'https://luma.joseon.space/api/v1/media/' + buildingData.thumbnail">

    <!-- Twitter -->
    <meta property="twitter:card" content="summary_large_image">
    <meta name="twitter:site" content="@joseonspace">
    <meta property="twitter:title"
          :content="buildingData.name + ' (' + palaceDict[selectedPalace] + ') - ' + langData.title">
    <meta property="twitter:description" :content="buildingData.explanation?.substring(0, 150)">
    <meta property="twitter:image" :content="'https://luma.joseon.space/api/v1/media/' + buildingData.thumbnail">

    <!-- Link tags to other pages -->
    <link rel="alternate" hreflang="ko" :href="`https://luma.joseon.space/${palaceURL[selectedPalace]}/${buildingSlug}`"
          v-if="selectedPalace !== '0' && lang !== 'ko' && buildingSlug !== ''"/>
    <link rel="alternate" hreflang="en" :href="`https://luma.joseon.space/${palaceURL[selectedPalace]}/${buildingSlug}`"
          v-if="selectedPalace !== '0' && lang !== 'en' && buildingSlug !== ''"/>
    <link rel="alternate" hreflang="ja" :href="`https://luma.joseon.space/${palaceURL[selectedPalace]}/${buildingSlug}`"
          v-if="selectedPalace !== '0' && lang !== 'ja' && buildingSlug !== ''"/>
    <link rel="alternate" hreflang="zh" :href="`https://luma.joseon.space/${palaceURL[selectedPalace]}/${buildingSlug}`"
          v-if="selectedPalace !== '0' && lang !== 'zh' && buildingSlug !== ''"/>

    <!-- Image Schema -->
    <component :is="'script'" type="application/ld+json">
      {{ imageMeta }}
    </component>
    <!-- Video Schema -->
    <component :is="'script'" type="application/ld+json">
      {{ videoMeta }}
    </component>

    <!-- Breadcrumb Schema -->
    <component :is="'script'" type="application/ld+json">
      {
      "@context": "https://schema.org",
      "@type": "BreadcrumbList",
      "itemListElement": [{
      "@type": "ListItem",
      "position": 1,
      "name": "Home",
      "item": "https://luma.joseon.space"
      },{
      "@type": "ListItem",
      "position": 2,
      "name": "{{ palaceDict[selectedPalace] }}",
      "item": "https://luma.joseon.space/{{ palaceURL[selectedPalace] }}"
      },{
      "@type": "ListItem",
      "position": 3,
      "name": "{{ building }}"
      }]
      }
    </component>

    <!-- Article Schema -->
    <component :is="'script'" type="application/ld+json">
      {
      "@context": "https://schema.org",
      "@type": "Article",
      "headline": "{{ buildingData.name }} ({{ palaceDict[selectedPalace] }})",
      "image": [
      "{{ 'https://luma.joseon.space/api/v1/media/' + buildingData.thumbnail }}"
      ],
      "datePublished": "2023-12-31T09:00:00+09:00",
      "author": [{
      "@type": "Organization",
      "name": "문화재청",
      "url": "https://www.cha.go.kr"
      }]
      }
    </component>
  </Teleport>

  <Transition name="opacity">
    <div class="fixed top-0 left-0 w-full h-full z-[2] overflow-y-scroll px-4 backdrop-blur-lg bg-base-100/50"
         v-show="showDetail" @click.self="closeDetail">
      <transition name="bounce">
        <div class="w-full rounded-box bg-base-100 mt-20 mb-32 h-auto relative mx-auto max-w-4xl"
             v-show="showDetail">

          <!-- Sticky container for the close button -->
          <div class="sticky top-0 z-10">
            <!-- Absolute positioned close button -->
            <div class="absolute right-4 top-4">
              <button class="btn btn-circle btn-sm" @click="closeDetail" aria-label="Close detail">
                <XMarkIcon class="w-5 h-auto"/>
              </button>
            </div>

          </div>

          <!-- Image container -->
          <header class="mb-4">
            <figure class="h-[50vh] max-h-[32rem] overflow-hidden rounded-box rounded-b-none mb-8"
                    :class="{ 'skeleton': !imageLoaded.thumbnail }">
              <img v-if="buildingData.thumbnail" :src="'/api/v1/media/' + buildingData.thumbnail"
                   :alt="buildingData.name" class="w-full h-full object-cover"
                   @load="imageLoaded.thumbnail = true">
            </figure>

            <h1 class="text-4xl md:text-5xl font-bold p-4 md:px-12">
              {{ buildingData.name }}
            </h1>

            <div class="flex px-4 md:px-12 gap-2 pb-4">
              <!-- Readtime is claculated by avraging 200 words per minute and show minutes and seconds rounded to nerest 5 seconds -->
              <div class="badge badge-primary drop-shadow-sm" v-if="buildingData.explanation">
                {{ (readingMinutes > 0) ? readingMinutes + langData.minute : '' }}
                {{ (readingSeconds > 0) ? readingSeconds + langData.second : '' }}
                {{ langData.readingtime }}
              </div>
              <div class="badge badge-primary drop-shadow-sm"
                   v-if="buildingData.detail_image && buildingData.detail_image.length > 0">
                {{ buildingData.detail_image.length }} {{
                  (buildingData.detail_image.length > 1) ?
                      langData.photos_plural : langData.photos
                }}
              </div>
              <div class="badge badge-primary drop-shadow-sm"
                   v-if="buildingData.detail_video && buildingData.detail_video.length > 0">
                {{ buildingData.detail_video.length }} {{
                  (buildingData.detail_video.length > 1) ?
                      langData.videos_plural : langData.videos
                }}
              </div>
            </div>
          </header>

          <main>
            <!-- Content -->
            <article>
              <h2 class="text-2xl md:text-3xl font-bold pt-0 p-4 md:px-12" v-if="detailImages.length > 0">
                {{ langData.quickoverview }}
              </h2>
              <!-- Additional images and videos -->
              <div class="carousel carousel-end w-full px-2 md:px-10 overflow-x-scroll overflow-y-visible pb-4"
                   v-if="detailImages.length > 0">

                <div class="carousel-item" v-for="image in detailImages">
                  <section
                      class="card h-96 overflow-hidden bg-base-100 shadow-md rounded-lg max-w-80 w-[70vw] cursor-pointer mx-2">
                    <div :class="{ 'skeleton': !image.imageLoaded }" class="w-full h-2/3">
                      <img :src="'/api/v1/media/' + image.media"
                           :alt="image.name + '\n' + image.explanation" loading="lazy"
                           class="w-full h-full object-cover" @load="image.imageLoaded = true">
                    </div>
                    <div class="absolute bottom-0 w-full p-4 bg-base-100/80 backdrop-blur-lg">
                      <h3 class="text-lg w-full font-semibold truncate mb-2">{{ image.name }}</h3>
                      <div class="h-32">
                        <p class="text-sm w-full ellipsis-multi-6 font-serif font-thin">{{
                            image.explanation
                          }}
                        </p>
                      </div>
                    </div>
                  </section>
                </div>
              </div>

              <h2 class="text-2xl md:text-3xl font-bold p-4 md:px-12">
                {{ langData.detail }}
              </h2>

              <div class="px-4 md:px-12" v-if="buildingData.explanation">
                <p class="font-serif font-thin leading-7 md:leading-9"
                   v-for="line in buildingData.explanation.split('\n')">
                  {{ line }}
                </p>
              </div>


              <h2 class="text-2xl md:text-3xl font-bold p-4 md:px-12" v-if="detailVideos.length > 0">
                {{ langData.multimedia }}
              </h2>

              <div class="carousel carousel-end w-full px-2 md:px-10 overflow-x-scroll overflow-y-visible pb-4"
                   v-if="detailVideos.length > 0">
                <div class="carousel-item" v-for="video in detailVideos" :key="video.video" :id="video.video">
                  <section @mouseover="hover = true" @mouseleave="hover = false"
                           class="card h-72 overflow-hidden bg-base-100 shadow-md rounded-lg max-w-96 w-[80vw] cursor-pointer mx-2 relative">
                    <!-- Video container with hover effect and fullscreen button -->
                    <div :class="{ 'skeleton': !video.Loaded }"
                         class="w-full h-full rounded-box rounded-b-none mb-4 relative">
                      <video :src="'/api/v1/media/' + video.video" muted autoplay loop
                             playsinline preload="auto" class="w-full h-7/8 object-cover"
                             @loadedmetadata="video.Loaded = true" ref="videoPlayer"></video>

                      <!-- Fullscreen button -->
                      <button @click="toggleFullscreen(video.video)" aria-label="Toggle video fullscreen"
                              class="absolute top-0 right-0 m-2 btn btn-circle btn-sm">
                        <ArrowsPointingOutIcon class="w-5 h-auto"/>
                      </button>
                    </div>
                    <div class="absolute bottom-0 w-full p-4 bg-base-100/80 backdrop-blur-md">
                      <h3 class="text-lg w-full font-semibold truncate">{{ video.name }}</h3>
                    </div>
                  </section>
                </div>
              </div>
            </article>
          </main>
          <div class=" h-10"></div>
        </div>
      </transition>
    </div>
  </Transition>
</template>

<style>
.bounce-enter-active {
  transition: all 0.3s cubic-bezier(.7, .14, .37, .93);
}

.bounce-leave-active {
  transition: all 0.3s cubic-bezier(.14, .74, .63, 1.08);
}

.bounce-enter-from,
.bounce-leave-to {
  transform: translateY(100vh);
  opacity: 0;
}

.opacity-enter-active {
  transition: opacity 0.3s ease-in-out;
}

.opacity-leave-active {
  transition: opacity 0.3s ease-in-out;
}

.opacity-enter-from,
.opacity-leave-to {
  opacity: 0;
}
</style>

<script setup>
import {ref, inject, defineProps, onMounted, onUnmounted, defineEmits, watch, computed} from 'vue';
import {XMarkIcon, ArrowsPointingOutIcon} from '@heroicons/vue/24/solid';

const props = defineProps(['building'])
const lang = inject('lang');
const selectedPalace = inject('selectedPalace');
const buildingSlug = inject('buildingSlug');
const langData = inject('langData');
const palaceDict = inject('palaceDict');
const palaceURL = inject('palaceURL');

const imageLoaded = ref({
  thumbnail: false,
});
const buildingData = ref({});
const showDetail = ref(false);
const detailImages = ref([]);
const detailVideos = ref([]);
const playing_video = ref('');
const readingSpeed = {
  "ko": 900,
  "en": 1200,
  "ja": 360,
  "zh": 255
};

const charCount = computed(() => buildingData.value.explanation?.length || 0);
const readingMinutes = computed(() => Math.round(charCount.value / readingSpeed[lang.value]) || 0);
const readingSeconds = computed(() => Math.round(charCount.value / readingSpeed[lang.value] * 60) % 60 || 0);

const imageMeta = ref([]);
const videoMeta = ref([]);

const generateImageMeta = () => {
  imageMeta.value = [];
  // add all the images in the detailImages array
  detailImages.value.forEach((image) => {
    imageMeta.value.push({
      "@context": "https://schema.org/",
      "@type": "ImageObject",
      "contentUrl": 'https://luma.joseon.space/api/v1/media/' + image.media,
      "license": 'https://www.kogl.or.kr/info/license.do',
      "acquireLicensePage": 'https://www.kogl.or.kr/info/license.do',
      "creditText": "Korea Cultural Heritage Administratio (문화재청)",
      "creator": {
        "@type": "Organization",
        "name": "문화재청",
      },
      "copyrightNotice": "문화재청",
    })
  })
}

const generateVideoMeta = () => {
  videoMeta.value = [];
  // add all the videos in the detailVideos array
  detailVideos.value.forEach((video) => {
    videoMeta.value.push({
      "@context": "https://schema.org",
      "@type": "VideoObject",
      "name": video.name,
      "description": video.name,
      "contentUrl": 'https://luma.joseon.space/api/v1/media/' + video.video,
      "embedUrl": 'https://luma.joseon.space/api/v1/media/' + video.video,
      "thumbnailUrl": 'https://luma.joseon.space/api/v1/media/' + video.video,
      "uploadDate": "2023-12-31T09:00:00+09:00",
    })
  })
}

const updateTitle = () => {
  document.title = palaceDict.value[selectedPalace.value] + ' - ' + buildingData.value.name + ' - ' + langData.title;
}

const fetchData = async (endpoint) => {
  try {
    const response = await fetch(new URL(endpoint, window.location.origin));
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error(`Error fetching data from ${endpoint}:`, error);
  }
};

const fetchBuildingData = async () => {
  if (buildingSlug.value === '') {
    closeDetail();
    return;
  }

  buildingData.value = await fetchData(window.location.origin + '/api/v1/buildingurl/?language=' + lang.value + '&building_name=' + props.building);
  await fetchDetailImages();
  await fetchDetailVideos();
  updateTitle();
}

const fetchDetailImages = async () => {
  if (!buildingData.value.detail_image?.length) return;
  await fetchDetails('photo', buildingData.value.detail_image, detailImages);
  generateImageMeta();
};

const fetchDetailVideos = async () => {
  if (!buildingData.value.detail_video?.length) return;
  await fetchDetails('video', buildingData.value.detail_video, detailVideos);
  generateVideoMeta();
};

const fetchDetails = async (type, ids, detailRef) => {
  const fetchPromises = ids.map(id =>
      fetchData(new URL("api/v1/" + type + "/?language=" + lang.value + "&" + type + "_id=" + id, window.location.origin))
  );
  detailRef.value = await Promise.all(fetchPromises);
};

const emit = defineEmits(['close']);

const closeDetail = () => {
  showDetail.value = false;
  setTimeout(() => emit('close'), 400);
}

const handleKeyDown = (event) => {
  if (event.key === 'Escape') closeDetail();
}

const handleFullscreenChange = () => {
  if (!document.fullscreenElement && playing_video.value) {
    const videoElement = videoPlayer.value;
    if (videoElement) videoElement.muted = true;
    playing_video.value = '';
  }
};

const enterFullscreen = (videoElement) => {
  videoElement.requestFullscreen?.() || videoElement.mozRequestFullScreen?.() || videoElement.webkitRequestFullscreen?.() || videoElement.msRequestFullscreen?.();
};

const exitFullscreen = () => {
  if (document.fullscreenElement) document.exitFullscreen();
};

watch(playing_video, (videoId) => {
  const videoElement = videoPlayer.value;
  if (!videoElement) return;
  if (videoId && !document.fullscreenElement) {
    enterFullscreen(videoElement);
    videoElement.muted = false;
  } else {
    exitFullscreen();
    videoElement.muted = true;
  }
});

const toggleFullscreen = (videoId) => {
  playing_video.value = playing_video.value === videoId ? '' : videoId;
};

onMounted(() => {
  showDetail.value = true;
  window.addEventListener('keydown', handleKeyDown);
  document.addEventListener('fullscreenchange', handleFullscreenChange);
  watch([lang, buildingSlug], fetchBuildingData);
  watch(selectedPalace, closeDetail);
  watch([buildingData, lang, selectedPalace], updateTitle);
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeyDown);
  document.removeEventListener('fullscreenchange', handleFullscreenChange);
});

fetchBuildingData();
</script>