import {reactive, ref} from 'vue';

export const useLanguageStore = () => {
    const lang = ref('en');
    const langData = reactive({
        title: "Luma",
        joseonSpace: "Joseon Space Luma",
        themeTooltip: "Toggle light/dark theme",
        searchPlaceholder: "Search all notices",
        scrollForRecent: "Scroll down browse recent news",
        indexCount: "article indexed & translated"
    });

    // Function to detect browser language
    const detectBrowserLanguage = () => {
        const browserLang = navigator.language || navigator.userLanguage;
        if (browserLang) {
            if (browserLang.startsWith('zh')) {
                lang.value = 'zh';
            } else if (browserLang.startsWith('ja')) {
                lang.value = 'ja';
            } else if (browserLang.startsWith('ko')) {
                lang.value = 'ko';
            } else {
                lang.value = 'en';
            }
        }
        console.log("Using auto detected language:", lang.value);
    }

    // Function to fetch language configuration
    const fetchLanguageConfig = async () => {
        try {
            const response = await fetch('/api/v1/languages/?language=' + lang.value);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const responseData = await response.json(); // Parsing the JSON response
            Object.assign(langData, responseData); // Correctly updating langData with parsed JSON
            console.log("Fetched language config:", lang.value);
        } catch (error) {
            console.error("Error while fetching language config:", error);
        }
    };

    // Function to save language to local storage
    const saveLanguageToLocalStorage = (language) => {
        localStorage.setItem('userLanguage', language);
    }
    const changeLanguage = (newLang) => {
        if (newLang !== lang.value) {
            console.log("Changing language to:", newLang);
            lang.value = newLang;
            fetchLanguageConfig();
            saveLanguageToLocalStorage(newLang);
        }
    }

    // On mounted
    onBeforeMount(() => {
        const storedLang = localStorage.getItem('userLanguage');
        if (storedLang) {
            lang.value = storedLang;
            console.log("Using stored language:", lang.value);
        } else {
            detectBrowserLanguage();
        }
        fetchLanguageConfig();
    });
    return {lang, langData, changeLanguage, detectBrowserLanguage, fetchLanguageConfig};
};
