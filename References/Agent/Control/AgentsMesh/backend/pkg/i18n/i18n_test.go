package i18n

import (
	"context"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestDefaultConfig(t *testing.T) {
	cfg := DefaultConfig()

	assert.Equal(t, "en", cfg.DefaultLocale)
	assert.Equal(t, []string{"en"}, cfg.FallbackChain)
}

func TestNew(t *testing.T) {
	t.Run("should create with nil config using defaults", func(t *testing.T) {
		i, err := New(nil)
		require.NoError(t, err)
		assert.NotNil(t, i)
		assert.Equal(t, "en", i.GetLocale())
	})

	t.Run("should create with custom config", func(t *testing.T) {
		cfg := &Config{
			DefaultLocale: "zh",
			FallbackChain: []string{"zh", "en"},
		}
		i, err := New(cfg)
		require.NoError(t, err)
		assert.NotNil(t, i)
	})
}

func TestI18n_LoadLocaleFromJSON(t *testing.T) {
	i, err := New(nil)
	require.NoError(t, err)

	t.Run("should load simple translations", func(t *testing.T) {
		json := `{"hello": "Hello", "world": "World"}`
		err := i.LoadLocaleFromJSON("test", []byte(json))
		require.NoError(t, err)

		assert.Equal(t, "Hello", i.TWithLocale("test", "hello"))
		assert.Equal(t, "World", i.TWithLocale("test", "world"))
	})

	t.Run("should load nested translations", func(t *testing.T) {
		json := `{"messages": {"greeting": "Hi", "farewell": "Bye"}}`
		err := i.LoadLocaleFromJSON("nested", []byte(json))
		require.NoError(t, err)

		assert.Equal(t, "Hi", i.TWithLocale("nested", "messages.greeting"))
		assert.Equal(t, "Bye", i.TWithLocale("nested", "messages.farewell"))
	})

	t.Run("should extract locale name from _name key", func(t *testing.T) {
		json := `{"_name": "Test Language", "key": "value"}`
		err := i.LoadLocaleFromJSON("named", []byte(json))
		require.NoError(t, err)

		locales := i.GetAvailableLocales()
		var found bool
		for _, l := range locales {
			if l.Code == "named" {
				assert.Equal(t, "Test Language", l.Name)
				found = true
				break
			}
		}
		assert.True(t, found)
	})

	t.Run("should handle invalid JSON", func(t *testing.T) {
		err := i.LoadLocaleFromJSON("invalid", []byte("not json"))
		assert.Error(t, err)
	})
}

func TestI18n_SetLocale(t *testing.T) {
	i, err := New(nil)
	require.NoError(t, err)

	t.Run("should set existing locale", func(t *testing.T) {
		// 'en' should be loaded from embedded locales
		err := i.SetLocale("en")
		require.NoError(t, err)
		assert.Equal(t, "en", i.GetLocale())
	})

	t.Run("should error for non-existent locale", func(t *testing.T) {
		err := i.SetLocale("nonexistent")
		assert.Error(t, err)
	})
}

func TestI18n_T(t *testing.T) {
	i, err := New(nil)
	require.NoError(t, err)

	// Load test locale
	json := `{"greeting": "Hello %s!", "count": "You have %d items"}`
	err = i.LoadLocaleFromJSON("test", []byte(json))
	require.NoError(t, err)
	err = i.SetLocale("test")
	require.NoError(t, err)

	t.Run("should translate simple key", func(t *testing.T) {
		json := `{"simple": "Simple text"}`
		err := i.LoadLocaleFromJSON("simple", []byte(json))
		require.NoError(t, err)

		result := i.TWithLocale("simple", "simple")
		assert.Equal(t, "Simple text", result)
	})

	t.Run("should format with string argument", func(t *testing.T) {
		result := i.T("greeting", "World")
		assert.Equal(t, "Hello World!", result)
	})

	t.Run("should format with integer argument", func(t *testing.T) {
		result := i.T("count", 5)
		assert.Equal(t, "You have 5 items", result)
	})

	t.Run("should return key if not found", func(t *testing.T) {
		result := i.T("nonexistent.key")
		assert.Equal(t, "nonexistent.key", result)
	})
}

func TestI18n_TWithLocale(t *testing.T) {
	i, err := New(nil)
	require.NoError(t, err)

	// Load multiple locales
	enJson := `{"hello": "Hello"}`
	zhJson := `{"hello": "你好"}`
	err = i.LoadLocaleFromJSON("en", []byte(enJson))
	require.NoError(t, err)
	err = i.LoadLocaleFromJSON("zh", []byte(zhJson))
	require.NoError(t, err)

	t.Run("should translate with specific locale", func(t *testing.T) {
		assert.Equal(t, "Hello", i.TWithLocale("en", "hello"))
		assert.Equal(t, "你好", i.TWithLocale("zh", "hello"))
	})

	t.Run("should fallback to fallback chain", func(t *testing.T) {
		// Key only exists in English
		enOnlyJson := `{"en_only": "English only"}`
		err := i.LoadLocaleFromJSON("en", []byte(enOnlyJson))
		require.NoError(t, err)

		// Request in zh, should fall back to en
		result := i.TWithLocale("zh", "en_only")
		assert.Equal(t, "English only", result)
	})
}

func TestI18n_GetAvailableLocales(t *testing.T) {
	i, err := New(nil)
	require.NoError(t, err)

	locales := i.GetAvailableLocales()
	assert.NotEmpty(t, locales)

	// Should have at least 'en' from embedded locales
	var hasEn bool
	for _, l := range locales {
		if l.Code == "en" {
			hasEn = true
			break
		}
	}
	assert.True(t, hasEn, "should have English locale")
}

func TestWithLocale(t *testing.T) {
	ctx := context.Background()

	t.Run("should store locale in context", func(t *testing.T) {
		ctx = WithLocale(ctx, "zh")
		locale := GetLocaleFromContext(ctx)
		assert.Equal(t, "zh", locale)
	})

	t.Run("should return empty for context without locale", func(t *testing.T) {
		locale := GetLocaleFromContext(context.Background())
		assert.Equal(t, "", locale)
	})
}

func TestI18n_TFromContext(t *testing.T) {
	i, err := New(nil)
	require.NoError(t, err)

	// Load test locales
	enJson := `{"msg": "English message"}`
	zhJson := `{"msg": "中文消息"}`
	err = i.LoadLocaleFromJSON("en", []byte(enJson))
	require.NoError(t, err)
	err = i.LoadLocaleFromJSON("zh", []byte(zhJson))
	require.NoError(t, err)
	err = i.SetLocale("en")
	require.NoError(t, err)

	t.Run("should use locale from context", func(t *testing.T) {
		ctx := WithLocale(context.Background(), "zh")
		result := i.TFromContext(ctx, "msg")
		assert.Equal(t, "中文消息", result)
	})

	t.Run("should fall back to current locale if context has no locale", func(t *testing.T) {
		result := i.TFromContext(context.Background(), "msg")
		assert.Equal(t, "English message", result)
	})
}

func TestFlattenTranslations(t *testing.T) {
	t.Run("should flatten nested structure", func(t *testing.T) {
		data := map[string]interface{}{
			"level1": map[string]interface{}{
				"level2": map[string]interface{}{
					"key": "deep value",
				},
				"key": "shallow value",
			},
			"top": "top value",
		}

		result := make(map[string]string)
		flattenTranslations("", data, result)

		assert.Equal(t, "deep value", result["level1.level2.key"])
		assert.Equal(t, "shallow value", result["level1.key"])
		assert.Equal(t, "top value", result["top"])
	})

	t.Run("should handle empty data", func(t *testing.T) {
		data := map[string]interface{}{}
		result := make(map[string]string)
		flattenTranslations("", data, result)

		assert.Empty(t, result)
	})
}

func TestFormatTranslation(t *testing.T) {
	t.Run("should return template without args", func(t *testing.T) {
		result := formatTranslation("Hello World")
		assert.Equal(t, "Hello World", result)
	})

	t.Run("should format with args", func(t *testing.T) {
		result := formatTranslation("Hello %s, you have %d messages", "Alice", 5)
		assert.Equal(t, "Hello Alice, you have 5 messages", result)
	})
}
