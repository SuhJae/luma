import { reactive, ref, onMounted } from 'vue';
import axios from 'axios';

const apiOrigin = "http://127.0.0.1:8000/"

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
    }

    // Function to fetch language configuration
    const fetchLanguageConfig = async () => {
        try {
            console.log("Fetching language config: " + lang.value);
            const response = await axios.get(apiOrigin + "api/v1/languages/", { params: { language: lang.value } });
            const responseData = JSON.parse(response.data[0]); // Parse the JSON string
            Object.assign(langData, responseData);
        } catch (error) {
            console.error("Error fetching language config:", error);
        }
    }

    // Function to save language to local storage
    const saveLanguageToLocalStorage = (language) => {
        localStorage.setItem('userLanguage', language);
    }


    const changeLanguage = (newLang) => {
        if (newLang !== lang.value) {
            lang.value = newLang;
            fetchLanguageConfig();
            saveLanguageToLocalStorage(newLang);
        }
    }

    // On mounted
    onMounted(() => {
        const storedLang = localStorage.getItem('userLanguage');
        if (storedLang) {
            lang.value = storedLang;
        } else {
            detectBrowserLanguage();
        }
        fetchLanguageConfig();
    });

    return { lang, langData, changeLanguage, detectBrowserLanguage, fetchLanguageConfig };
};
