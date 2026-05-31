# План разработки лендинга для Voice-to-Text

## Обзор проекта

**Voice-to-Text** — десктопное приложение для преобразования голоса в текст с фокусом на приватность и офлайн-поддержку. Построено на Tauri, Rust и Vue 3.

### Ключевые особенности приложения:
- 🎤 **Real-time транскрипция** с поддержкой нескольких провайдеров (Deepgram, AssemblyAI, Whisper)
- 🔒 **Privacy-focused** — API ключи хранятся локально, нет облачного хранилища
- 🌍 **Кроссплатформенность** — macOS, Windows, Linux
- ⚡ **Глобальные хоткеи** — быстрый доступ через горячие клавиши
- 📋 **Автоматическое копирование** в буфер обмена
- 🎨 **Современный UI** с glass morphism эффектами
- 🌐 **Мультиязычность** — поддержка 6 языков (en, ru, es, fr, de, uk)

---

## Технологический стек

### Основные технологии:
- **Nuxt 3** — фреймворк для Vue.js с SSR/SSG
- **Vuetify 3** — Material Design компоненты
- **Vue I18n** — локализация (совместимо с текущим `vue-i18n`)
- **TypeScript** — типизация
- **Vite** — сборщик (встроен в Nuxt)
- **Pinia** — управление общим состоянием (через `@pinia/nuxt`)

### Дополнительные библиотеки:
- **@nuxtjs/i18n** — интеграция i18n с Nuxt
- **@nuxtjs/seo** — SEO оптимизация
- **@vueuse/nuxt** — композаблы для Vue (например `usePreferredDark`)
- **nuxt-icon** — иконки
- **@nuxtjs/ipx** — обработка изображений (опционально)
- **swiper** — карусель скриншотов (Vue интеграция)
- **@nuxt/eslint** + **Prettier** — линтинг и форматирование кода

Примечания по зависимостям:
- Google Fonts лучше не подключать как внешнюю зависимость. Либо системный шрифт, либо self-host (проще с приватностью и стабильностью).

---

## Архитектура проекта

```
landing/
├── data/                        # статические данные/конфиги секций (без Nuxt контекста)
├── types/                       # TS типы (без Nuxt контекста)
├── utils/                       # чистые функции (без Nuxt контекста, легко тестировать)
├── nuxt.config.ts              # Конфигурация Nuxt
├── package.json
├── tsconfig.json
├── .env                        # Переменные окружения
│
├── locales/                    # Файлы локализации
│   ├── en.json
│   ├── ru.json
│   ├── es.json
│   ├── fr.json
│   ├── de.json
│   └── uk.json
│
├── assets/                     # Статические ресурсы
│   ├── images/
│   │   ├── hero-bg.jpg
│   │   ├── screenshot-dark.png
│   │   ├── screenshot-light.png
│   │   ├── features/
│   │   └── platforms/
│   ├── videos/                 # Демо-видео (опционально)
│   └── styles/
│       └── main.scss           # Глобальные стили
│
├── components/                 # Vue компоненты
│   ├── layout/
│   │   ├── AppHeader.vue       # Шапка с навигацией
│   │   ├── AppFooter.vue       # Подвал
│   │   └── LanguageSwitcher.vue # Переключатель языков
│   │
│   ├── sections/
│   │   ├── HeroSection.vue     # Главный экран
│   │   ├── FeaturesSection.vue  # Особенности
│   │   ├── ProvidersSection.vue # STT провайдеры
│   │   ├── ScreenshotsSection.vue # Скриншоты
│   │   ├── DownloadSection.vue  # Секция загрузки
│   │   ├── PrivacySection.vue   # Приватность
│   │   └── FAQSection.vue       # Частые вопросы
│   │
│   ├── ui/
│   │   ├── DownloadButton.vue   # Кнопка загрузки
│   │   ├── FeatureCard.vue      # Карточка фичи
│   │   ├── PlatformBadge.vue    # Бейдж платформы
│   │   └── ScreenshotCarousel.vue # Карусель скриншотов
│   │
│   └── common/
│       ├── AppLogo.vue
│       └── ThemeToggle.vue      # Переключатель темы (если нужен)
│
├── composables/                # Композаблы
│   ├── useDownload.ts          # Логика загрузки
│   ├── useAnalytics.ts         # Аналитика (опционально)
│   ├── usePlatform.ts          # Определение платформы
│   ├── useBrowserTheme.ts      # Определение темы браузера
│   └── useLocation.ts          # Определение локации пользователя
│
├── layouts/
│   └── default.vue             # Основной layout
│
├── plugins/                    # Плагины Nuxt
│   ├── vuetify.ts              # Инициализация Vuetify
│   └── init-theme-locale.client.ts # Автоинициализация темы и локали
│
├── pages/
│   ├── index.vue               # Главная страница
│   ├── download.vue            # Страница загрузки
│   └── privacy.vue             # Политика приватности (опционально)
│
├── public/                     # Публичные файлы
│   ├── favicon.ico
│   ├── robots.txt
│   └── sitemap.xml
│
└── server/                     # Server API (если нужен)
```

---

## Правила разделения логики

- **composables/**: завязаны на Nuxt/Vue (реактивность, `useCookie`, `navigateTo`, `useRoute`, `useFetch`, `useHead` и т.д.)
- **utils/**: чистые функции без Nuxt контекста (легко тестировать, переиспользовать)

## Структура страниц

### 1. Главная страница (`/`)

#### Hero Section
- **Заголовок**: "Voice to Text — Privacy-Focused Transcription"
- **Подзаголовок**: Краткое описание приложения
- **CTA кнопки**:
  - "Download for [Platform]" (определяется автоматически)
  - "View Features" (скролл к секции)
- **Фоновое изображение/видео**: Демонстрация приложения

#### Features Section
**6 основных фич в виде карточек:**

1. **Real-time Transcription**
   - Иконка: 🎤
   - Описание: Мгновенная транскрипция с частичными результатами

2. **Privacy-Focused**
   - Иконка: 🔒
   - Описание: API ключи хранятся локально, нет облачного хранилища

3. **Multiple Providers**
   - Иконка: 🌐
   - Описание: Deepgram, AssemblyAI, Whisper (офлайн)

4. **Cross-Platform**
   - Иконка: 💻
   - Описание: macOS, Windows, Linux

5. **Global Hotkeys**
   - Иконка: ⌨️
   - Описание: Быстрый доступ через горячие клавиши

6. **Auto-Copy**
   - Иконка: 📋
   - Описание: Автоматическое копирование в буфер обмена

#### Providers Section
**Детальное описание STT провайдеров:**

- **Deepgram** (Nova-2/3)
  - Низкая задержка
  - Высокое качество
  - Автоматический выбор модели (Nova-3 для английского, Nova-2 для русского)

- **AssemblyAI** (Universal-Streaming v3)
  - Высокое качество
  - Облачный сервис

- **Whisper Local** (офлайн)
  - Полностью офлайн
  - Требует cmake и загрузки модели

#### Screenshots Section
**Карусель скриншотов (Swiper):**
- Используем Swiper для Vue: `https://swiperjs.com/vue`
- На **десктопе** должно быть видно **сразу несколько** скриншотов на экране (не один с обязательным “далее”)
  - Пример: `slidesPerView: 2-4` на широких экранах с `breakpoints`
  - Допускается режим с “частичным” превью следующего слайда
- На мобильных: 1 скрин, свайп, пагинация
- Набор скринов:
  - Темная тема
  - Светлая тема
  - Настройки
  - Процесс записи

#### Download Section
**Платформо-специфичные кнопки загрузки с автоопределением ОС:**
- Определяем текущую ОС пользователя и показываем **приоритетно** релевантную загрузку
- Если ОС определить не удалось — показываем **все** ОС
- Для macOS учитывать архитектуру (Apple Silicon vs Intel):
  - Если получилось определить — выбираем нужную сборку по умолчанию
  - Если нет — показываем оба варианта и даём выбрать вручную

**Дополнительно:**
- Версия приложения
- Размер файла
- Системные требования
- Changelog ссылка

#### Privacy Section
**Ключевые моменты приватности:**
- Локальное хранение API ключей
- Нет облачного хранилища транскрипций
- Опциональное использование собственных API ключей

**Open Source:**
- Да: часть компонентов/модулей планируем сделать open-source (для маркетинга и доверия)

#### FAQ Section
**Частые вопросы:**
1. Какие платформы поддерживаются?
2. Нужен ли интернет для работы?
3. Как настроить API ключи?
4. Можно ли использовать офлайн?
5. Как изменить горячие клавиши?
6. Безопасны ли мои данные?

### 2. Страница загрузки (`/download`)

- **Определение платформы** автоматически
- **Кнопки загрузки** для всех платформ
- **Инструкции по установке** для каждой ОС
- **Системные требования**
- **Changelog** (последние версии)

---

## Локализация (i18n)

### Поддерживаемые языки:
- 🇺🇸 English (`en`)
- 🇷🇺 Русский (`ru`)
- 🇪🇸 Español (`es`)
- 🇫🇷 Français (`fr`)
- 🇩🇪 Deutsch (`de`)
- 🇺🇦 Українська (`uk`)

### Структура файлов локализации:

```json
// locales/en.json
{
  "meta": {
    "title": "Voice to Text - Privacy-Focused Transcription",
    "description": "..."
  },
  "nav": {
    "features": "Features",
    "download": "Download",
    "privacy": "Privacy"
  },
  "hero": {
    "title": "Voice to Text",
    "subtitle": "Privacy-focused voice-to-text application with offline support",
    "download": "Download for {platform}",
    "viewFeatures": "View Features"
  },
  "features": {
    "realtime": {
      "title": "Real-time Transcription",
      "description": "..."
    },
    "privacy": {
      "title": "Privacy-Focused",
      "description": "..."
    }
    // ... остальные фичи
  },
  "providers": {
    "title": "Multiple STT Providers",
    "deepgram": {
      "name": "Deepgram",
      "description": "..."
    }
    // ... остальные провайдеры
  },
  "download": {
    "title": "Download",
    "forPlatform": "Download for {platform}",
    "systemRequirements": "System Requirements",
    "version": "Version {version}"
  },
  "faq": {
    "title": "Frequently Asked Questions",
    "items": [
      {
        "question": "...",
        "answer": "..."
      }
    ]
  }
}
```

### Модель контента (чтобы i18n не превращалась в ад)

Проблема классическая: если хранить “структуру секций” в `data/*`, а весь контент раскидать по ключам i18n, то любая правка превращается в квест “найди 20 ключей в 6 языках”.

Решение — разделить два слоя:
- **Микрокопирайт** (кнопки, лейблы, мелкие подписи) — остаётся в `landing/locales/*`.
- **Контент секций** (FAQ, список фич, провайдеры, тексты блоков) — лежит в **локализованных контент-файлах** с одинаковой структурой по всем языкам.

Рекомендуемая схема:
- `landing/content/en.ts`, `landing/content/ru.ts`, ... (или `.json`, если удобнее).
- Внутри — один типизированный объект `LandingContent`, где:
  - элементы имеют **стабильные `id`** (например `faq.items[].id`, `features.items[].id`)
  - порядок можно менять без рефакторинга компонентов
  - длинные тексты редактируются “в одном месте” для каждой локали

Минимальные правила дисциплины:
- `id` неизменяемы (меняем текст, но не идентификатор).
- Если добавили/удалили элемент — правим **все локали** (это легко проверяется автоматикой).
- Для контента не используем “вложенные ключи на 10 уровней”, держим структуру простой и читаемой.

Проверка качества:
- Добавляем маленькую проверку (скрипт/тест), которая сравнивает структуру контента между локалями и падает, если где-то не хватает ключей/элементов.

Минимальный “контракт” этой проверки:
- сравниваем структуру (ключи/массивы по `id`), а не тексты
- ошибка должна показывать, **какой `id`/ключ отсутствует** и **в какой локали**
- проверка запускается локально и в CI (чтобы не ловить это уже на проде)

### Настройка i18n в Nuxt:

```typescript
// nuxt.config.ts
export default defineNuxtConfig({
  modules: [
    '@nuxtjs/i18n',
    'vuetify/nuxt'
  ],
  i18n: {
    locales: [
      { code: 'en', iso: 'en-US', file: 'en.json', name: 'English' },
      { code: 'ru', iso: 'ru-RU', file: 'ru.json', name: 'Русский' },
      { code: 'es', iso: 'es-ES', file: 'es.json', name: 'Español' },
      { code: 'fr', iso: 'fr-FR', file: 'fr.json', name: 'Français' },
      { code: 'de', iso: 'de-DE', file: 'de.json', name: 'Deutsch' },
      { code: 'uk', iso: 'uk-UA', file: 'uk.json', name: 'Українська' }
    ],
    defaultLocale: 'en',
    strategy: 'prefix_except_default',
    detectBrowserLanguage: {
      useCookie: true,
      cookieKey: 'i18n_redirected',
      redirectOn: 'root',
      // Определение языка по локации (через composable)
      alwaysRedirect: false,
      fallbackLocale: 'en'
    }
  }
})
```

### Автоматическое определение языка по локации:

Логика определения языка:
1. **Проверка cookie** — если пользователь уже выбирал язык, использовать его
2. **Определение по браузеру** — `navigator.language` или `navigator.languages`
3. **Fallback** — английский язык по умолчанию

Важно:
- Лендинг планируется как **SSG (статический)**. Значит IP-геолокация на сервере здесь неуместна: негде “серверу” исполняться на каждый запрос.
- Если когда-то понадобится geo-редирект — это отдельная задача (edge/runtime), не часть текущего лендинга.

**Маппинг стран к языкам:**
- 🇷🇺 Россия, Беларусь, Казахстан → `ru`
- 🇺🇦 Украина → `uk`
- 🇪🇸 Испания, Латинская Америка → `es`
- 🇫🇷 Франция, Бельгия, Швейцария (французский) → `fr`
- 🇩🇪 Германия, Австрия, Швейцария (немецкий) → `de`
- 🇺🇸 Остальные → `en`

---

## Компоненты Vuetify

### Используемые компоненты:

1. **v-app-bar** — шапка сайта
2. **v-container**, **v-row**, **v-col** — сетка
3. **v-card** — карточки фич
4. **v-btn** — кнопки
5. **v-carousel** — карусель скриншотов
6. **v-expansion-panels** — FAQ аккордеон
7. **v-chip** — бейджи платформ
8. **v-select** — выбор языка
9. **v-icon** — иконки
10. **v-divider** — разделители

### Кастомизация темы:

```typescript
// plugins/vuetify.ts
import { createVuetify } from 'vuetify'

export default defineNuxtPlugin((nuxtApp) => {
  // Определение темы браузера при инициализации
  const getInitialTheme = (): 'dark' | 'light' => {
    if (process.client) {
      // Проверка сохраненной темы в localStorage
      const savedTheme = localStorage.getItem('vuetify-theme')
      if (savedTheme === 'dark' || savedTheme === 'light') {
        return savedTheme
      }

      // Определение по системным настройкам браузера
      if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
        return 'dark'
      }
    }
    return 'light' // Fallback для SSR
  }

  const vuetify = createVuetify({
    theme: {
      defaultTheme: getInitialTheme(),
      themes: {
        dark: {
          colors: {
            primary: '#6366f1', // indigo
            secondary: '#8b5cf6', // purple
            accent: '#ec4899', // pink
            background: '#0f172a', // slate-900
            surface: '#1e293b', // slate-800
          }
        },
        light: {
          colors: {
            primary: '#6366f1',
            secondary: '#8b5cf6',
            accent: '#ec4899',
            background: '#ffffff',
            surface: '#f8fafc', // slate-50
          }
        }
      }
    }
  })

  // Слушатель изменений системной темы
  if (process.client) {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
    const handleThemeChange = (e: MediaQueryListEvent) => {
      const savedTheme = localStorage.getItem('vuetify-theme')
      // Автоматически менять только если пользователь не выбирал тему вручную
      if (!savedTheme) {
        vuetify.theme.global.name.value = e.matches ? 'dark' : 'light'
      }
    }
    mediaQuery.addEventListener('change', handleThemeChange)
  }

  nuxtApp.vueApp.use(vuetify)
})
```

---

## SEO оптимизация

### Meta теги:

```vue
<!-- layouts/default.vue -->
<template>
  <Html :lang="$i18n.locale">
    <Head>
      <Title>{{ $t('meta.title') }}</Title>
      <Meta name="description" :content="$t('meta.description')" />
      <Meta property="og:title" :content="$t('meta.title')" />
      <Meta property="og:description" :content="$t('meta.description')" />
      <Meta property="og:image" content="/og-image.png" />
      <Meta name="twitter:card" content="summary_large_image" />
    </Head>
    <!-- ... -->
  </Html>
</template>
```

### Структурированные данные (JSON-LD):

```typescript
// composables/useStructuredData.ts
export const useStructuredData = () => {
  const { $i18n } = useNuxtApp()

  const softwareApplication = {
    "@context": "https://schema.org",
    "@type": "SoftwareApplication",
    "name": "Voice to Text",
    "applicationCategory": "UtilityApplication",
    "operatingSystem": ["macOS", "Windows", "Linux"],
    "offers": {
      "@type": "Offer",
      "price": "0",
      "priceCurrency": "USD"
    }
  }

  return { softwareApplication }
}
```

---

## Функциональность

### 1. Определение платформы

```typescript
// composables/usePlatform.ts
export const usePlatform = () => {
  const platform = ref<'macos' | 'windows' | 'linux' | 'unknown'>('unknown')

  if (process.client) {
    const userAgent = navigator.userAgent.toLowerCase()
    if (userAgent.includes('mac')) platform.value = 'macos'
    else if (userAgent.includes('win')) platform.value = 'windows'
    else if (userAgent.includes('linux')) platform.value = 'linux'
  }

  const downloadUrl = computed(() => {
    // Логика формирования URL для загрузки
    const baseUrl = 'https://github.com/777genius/voice-to-text/releases'
    // ...
  })

  return { platform, downloadUrl }
}
```

### 2. Определение темы браузера

```typescript
// composables/useBrowserTheme.ts
import { usePreferredDark } from '@vueuse/core'
import { useTheme } from 'vuetify'

export const useBrowserTheme = () => {
  const { $vuetify } = useNuxtApp()
  const preferredDark = usePreferredDark()
  const theme = useTheme()

  // Инициализация темы при первом посещении
  const initTheme = () => {
    if (process.client) {
      const savedTheme = localStorage.getItem('vuetify-theme')

      if (savedTheme) {
        // Использовать сохраненную тему
        theme.global.name.value = savedTheme as 'dark' | 'light'
      } else {
        // Использовать системную тему браузера
        theme.global.name.value = preferredDark.value ? 'dark' : 'light'
        localStorage.setItem('vuetify-theme', theme.global.name.value)
      }
    }
  }

  // Переключение темы
  const toggleTheme = () => {
    const newTheme = theme.global.name.value === 'dark' ? 'light' : 'dark'
    theme.global.name.value = newTheme
    localStorage.setItem('vuetify-theme', newTheme)
  }

  // Установка конкретной темы
  const setTheme = (themeName: 'dark' | 'light') => {
    theme.global.name.value = themeName
    localStorage.setItem('vuetify-theme', themeName)
  }

  // Слушатель изменений системной темы (только если пользователь не выбирал вручную)
  if (process.client) {
    watch(preferredDark, (isDark) => {
      const savedTheme = localStorage.getItem('vuetify-theme')
      if (!savedTheme) {
        theme.global.name.value = isDark ? 'dark' : 'light'
      }
    })
  }

  return {
    currentTheme: computed(() => theme.global.name.value),
    isDark: computed(() => theme.global.name.value === 'dark'),
    initTheme,
    toggleTheme,
    setTheme
  }
}
```

### 3. Определение локации пользователя

```typescript
// composables/useLocation.ts
export const useLocation = () => {
  const { $i18n } = useNuxtApp()
  const locale = useCookie('i18n_redirected', { default: () => 'en' })

  // Маппинг стран к языкам
  const countryToLocale: Record<string, string> = {
    'RU': 'ru', // Россия
    'BY': 'ru', // Беларусь
    'KZ': 'ru', // Казахстан
    'UA': 'uk', // Украина
    'ES': 'es', // Испания
    'MX': 'es', // Мексика
    'AR': 'es', // Аргентина
    'CO': 'es', // Колумбия
    'CL': 'es', // Чили
    'PE': 'es', // Перу
    'FR': 'fr', // Франция
    'BE': 'fr', // Бельгия (французский)
    'CH': 'de', // Швейцария (по умолчанию немецкий, можно улучшить)
    'DE': 'de', // Германия
    'AT': 'de', // Австрия
  }

  // Определение языка по браузеру
  const getBrowserLocale = (): string => {
    if (process.client) {
      const browserLang = navigator.language || (navigator as any).userLanguage
      const langCode = browserLang.split('-')[0].toLowerCase()

      // Проверка поддерживаемых языков
      const supportedLocales = ['en', 'ru', 'es', 'fr', 'de', 'uk']
      if (supportedLocales.includes(langCode)) {
        return langCode
      }

      // Проверка полного кода (например, ru-RU)
      const fullCode = browserLang.toLowerCase()
      if (fullCode.startsWith('ru')) return 'ru'
      if (fullCode.startsWith('uk')) return 'uk'
      if (fullCode.startsWith('es')) return 'es'
      if (fullCode.startsWith('fr')) return 'fr'
      if (fullCode.startsWith('de')) return 'de'
    }
    return 'en'
  }

  // Важно: лендинг статический (SSG), поэтому IP-геолокацию не используем.

  // Инициализация языка при первом посещении
  const initLocale = async () => {
    // Если язык уже выбран пользователем, не менять
    if (locale.value && locale.value !== 'en') {
      return
    }

    // Приоритет: cookie > браузер > fallback
    let detectedLocale = locale.value || 'en'

    // На клиенте определяем по браузеру
    detectedLocale = getBrowserLocale()

    // Устанавливаем язык только если он отличается от текущего
    if (detectedLocale !== $i18n.locale.value) {
      const { switchLocalePath } = useI18n()
      await navigateTo(switchLocalePath(detectedLocale))
    }
  }

  return {
    currentLocale: computed(() => $i18n.locale.value),
    initLocale,
    getBrowserLocale
  }
}
```

### 4. Плагин для автоматической инициализации

```typescript
// plugins/init-theme-locale.client.ts
export default defineNuxtPlugin(async () => {
  const { initTheme } = useBrowserTheme()
  const { initLocale } = useLocation()

  // Инициализация темы
  initTheme()

  // Инициализация локали (только при первом посещении)
  const hasVisited = useCookie('has_visited', { default: () => false })
  if (!hasVisited.value) {
    await initLocale()
    hasVisited.value = true
  }
})
```

### 5. Статистика загрузок (опционально)

Не делаем.

### 6. Аналитика (опционально)

```typescript
// composables/useAnalytics.ts
export const useAnalytics = () => {
  const trackDownload = (platform: string) => {
    if (process.client) {
      // Google Analytics, Plausible, или другая аналитика
      gtag('event', 'download', { platform })
    }
  }

  return { trackDownload }
}
```

**Решение по аналитике:**
- Делаем **GA4** (Google Analytics) + события:
  - `download_click` (platform, arch, version, locale)
  - `download_page_view`
  - `language_change`
  - `theme_change`
  - `faq_open`
  - `cta_view_features_click`
- Для подключения нужен `GA4 Measurement ID` (например, `G-XXXXXXXXXX`) и/или доступы к аккаунту. В коде предусматриваем конфиг через env, а фактическое подключение выполняется владельцем аккаунта.

---

## Дизайн и стилизация

### Цветовая схема:

**Темная тема:**
- Фон: `#0f172a` (slate-900)
- Поверхности: `#1e293b` (slate-800)
- Акцент: `#6366f1` (indigo-500)
- Текст: `#f1f5f9` (slate-100)

**Светлая тема:**
- Фон: `#ffffff`
- Поверхности: `#f8fafc` (slate-50)
- Акцент: `#6366f1` (indigo-500)
- Текст: `#0f172a` (slate-900)

### Типографика:

- **Заголовки**: Inter или System Font Stack
- **Текст**: Inter или System Font Stack
- **Моноширинный**: JetBrains Mono (для кода)

### Анимации:

- Плавные переходы при скролле
- Hover эффекты на карточках
- Параллакс для hero секции (опционально)

---

## Деплой

### Рекомендуемые платформы:

1. **Vercel** (рекомендуется)
   - Автоматический деплой из Git
   - SSR/SSG поддержка
   - CDN по умолчанию

2. **Netlify**
   - Аналогично Vercel
   - Хорошая поддержка Nuxt

3. **GitHub Pages** (только SSG)
   - Бесплатный хостинг
   - Требует `nuxt generate`

### Target деплой:
- **Render**
- Режим: **Static Site Generation (SSG)** (статическая генерация)

### Конфигурация для деплоя:

```typescript
// nuxt.config.ts
export default defineNuxtConfig({
  // Для SSG (пререндер страниц, а не SPA):
  ssr: true,
  nitro: { preset: 'static' },
  routeRules: {
    '/': { prerender: true },
    '/download': { prerender: true },
  },
})
```

### Важно про i18n + SSG (критично для SEO)

`routeRules` выше — это только базовый пример. Для i18n нужно гарантировать, что **пререндерятся все локали**.

Правило:
- Источник правды — список локалей + список страниц.
- На их основе формируем список путей для пререндера и для sitemap.

Пример логики (идея, не финальный код):
- Локали: `['en', 'ru', 'es', 'fr', 'de', 'uk']`, default = `en`
- Страницы: `['/', '/download']`
- Генерация путей:
  - для `en`: `['/', '/download']`
  - для остальных: `['/ru', '/ru/download']`, `['/es', '/es/download']`, ...

Это решает сразу две проблемы:
- не теряем локали при деплое (все страницы реально существуют как статик)
- sitemap/alternate можно генерировать из той же таблицы

См. также: `landing/docs/ARCHITECTURE_GUARDRAILS.md` (раздел про “источник правды по URL”).

---

## Чеклист разработки

### Фаза 1: Настройка проекта
- [ ] Инициализация Nuxt 3 проекта
- [ ] Установка Vuetify 3
- [ ] Настройка TypeScript
- [ ] Настройка Pinia (`@pinia/nuxt`) и базовых stores (общие состояния не держим “размазанными” по компонентам)
- [ ] Настройка i18n с определением локации
- [ ] Настройка Vuetify с определением темы браузера
- [ ] Установка @vueuse/nuxt для usePreferredDark
- [ ] ESLint (`@nuxt/eslint`) + Prettier (единый стиль форматирования)
- [ ] Базовая структура папок

### Фаза 2: Layout и навигация
- [ ] Создание `default.vue` layout
- [ ] Компонент `AppHeader.vue` с навигацией
- [ ] Компонент `AppFooter.vue`
- [ ] Компонент `LanguageSwitcher.vue`
- [ ] Адаптивная навигация (мобильное меню)

### Фаза 3: Главная страница
- [ ] Hero Section
- [ ] Features Section (6 карточек)
- [ ] Providers Section
- [ ] Screenshots Section (карусель)
- [ ] Download Section
- [ ] Privacy Section
- [ ] FAQ Section

### Фаза 4: Локализация и тема
- [ ] Переводы для всех 6 языков
- [ ] Композабл `useBrowserTheme.ts` для определения темы
- [ ] Композабл `useLocation.ts` для определения локации
- [ ] Плагин `init-theme-locale.client.ts` для автоинициализации
- [ ] Маппинг стран к языкам
- [ ] Определение языка по браузеру (client-side)
- [ ] Определение темы по системным настройкам
- [ ] Сохранение выбора пользователя в cookies/localStorage
- [ ] Тестирование переключения языков и темы
- [ ] SEO мета-теги для каждого языка
- [ ] Правильные URL для каждого языка

### Фаза 5: Функциональность
- [ ] Определение платформы пользователя
- [ ] Кнопки загрузки с правильными ссылками
- [ ] Страница `/download` с инструкциями
- [ ] Аналитика (GA4) + события (скачивание, смена языка/темы, FAQ, CTA)

### Фаза 6: Оптимизация
- [ ] Оптимизация изображений
- [ ] Lazy loading для секций
- [ ] SEO оптимизация
- [ ] Структурированные данные
- [ ] Sitemap и robots.txt

### Фаза 7: Тестирование
- [ ] Тестирование на разных устройствах
- [ ] Тестирование всех языков
- [ ] Тестирование автоматического определения языка по браузеру
- [ ] Тестирование автоматического определения темы
- [ ] Тестирование переключения темы вручную
- [ ] Тестирование сохранения выбора пользователя
- [ ] Проверка производительности
- [ ] Проверка доступности (a11y)

### Фаза 8: Деплой
- [ ] Настройка CI/CD
- [ ] Деплой на выбранную платформу
- [ ] Настройка домена
- [ ] SSL сертификат

---

## Дополнительные рекомендации

### Определение темы и локации:
- **Приоритет определения языка:**
  1. Cookie (если пользователь уже выбирал)
  2. Браузерные настройки (`navigator.language`)
  3. Fallback на английский

- **Приоритет определения темы:**
  1. localStorage (если пользователь выбирал вручную)
  2. Системные настройки браузера (`prefers-color-scheme`)
  3. Fallback на светлую тему

- **Альтернативные API для геолокации:**
  - Не используем в рамках текущего статического лендинга (SSG).

- **Обработка ошибок:**
  - Таймаут для API запросов (3 секунды)
  - Graceful fallback на браузерные настройки
  - Логирование ошибок для отладки

### Производительность:
- Использовать `nuxt/image` для оптимизации изображений
- Lazy loading для компонентов ниже fold
- Code splitting для больших компонентов
 - Никаких внешних geo-запросов: меньше точек отказа и проще с приватностью.

### Доступность:
- Семантический HTML
- ARIA атрибуты
- Keyboard navigation
- Контрастность цветов (WCAG AA)

### Аналитика:
- Google Analytics 4
- Plausible (privacy-focused)
- Yandex Metrika (для русскоязычной аудитории)

### Мониторинг:
- Sentry для отслеживания ошибок
- Uptime monitoring

---

## Примеры реализации компонентов

### Hero Section

```vue
<template>
  <v-container class="hero-section">
    <v-row align="center" justify="center" class="fill-height">
      <v-col cols="12" md="8" class="text-center">
        <h1 class="text-h2 font-weight-bold mb-4">
          {{ $t('hero.title') }}
        </h1>
        <p class="text-h6 text-medium-emphasis mb-8">
          {{ $t('hero.subtitle') }}
        </p>
        <div class="d-flex gap-4 justify-center flex-wrap">
          <DownloadButton :platform="platform" />
          <v-btn
            size="large"
            variant="outlined"
            @click="scrollToFeatures"
          >
            {{ $t('hero.viewFeatures') }}
          </v-btn>
        </div>
      </v-col>
    </v-row>
  </v-container>
</template>
```

### Feature Card

```vue
<template>
  <v-card class="feature-card" elevation="2">
    <v-card-text class="text-center pa-6">
      <v-icon
        :icon="icon"
        size="64"
        color="primary"
        class="mb-4"
      />
      <h3 class="text-h6 mb-2">{{ title }}</h3>
      <p class="text-body-2 text-medium-emphasis">
        {{ description }}
      </p>
    </v-card-text>
  </v-card>
</template>
```

---

## Контакты и ресурсы

- **GitHub**: https://github.com/777genius/voice-to-text
- **Документация**: (если есть)
- **Поддержка**: (если есть)

---

**Версия плана**: 1.0
**Дата создания**: 2025-01-17
**Статус**: Готов к реализации

---

## План итераций (сначала планируем, затем перепроверяем, потом реализуем)

Процесс:
1) Сначала готовим максимально подробные планы итераций.
2) Затем **несколько раз** перепроверяем планы (полнота, несостыковки, риски, критерии готовности).
3) Только после этого начинаем реализацию пошагово.
4) После реализации — сверяемся с планами и ещё раз перепроверяем соответствие.

Файлы итераций:
- `landing/docs/iterations/ITERATION_00_REQUIREMENTS.md`
- `landing/docs/iterations/ITERATION_01_SCAFFOLDING.md`
- `landing/docs/iterations/ITERATION_02_UI_SECTIONS.md`
- `landing/docs/iterations/ITERATION_03_SWIPER_AND_DOWNLOAD.md`
- `landing/docs/iterations/ITERATION_04_ANALYTICS_SEO_SSG_RENDER.md`
