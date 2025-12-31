'use client';

interface LanguageSelectorProps {
  selectedLanguage: string;
  onLanguageChange: (language: string) => void;
}

export default function LanguageSelector({ selectedLanguage, onLanguageChange }: LanguageSelectorProps) {
  const languages = [
    { code: 'English', name: 'English', flag: '🇬🇧' },
    { code: 'Spanish', name: 'Español', flag: '🇪🇸' },
    { code: 'French', name: 'Français', flag: '🇫🇷' },
    { code: 'German', name: 'Deutsch', flag: '🇩🇪' },
    { code: 'Japanese', name: '日本語', flag: '🇯🇵' },
    { code: 'Chinese', name: '中文', flag: '🇨🇳' },
    { code: 'Hindi', name: 'हिन्दी', flag: '🇮🇳' },
    { code: 'Portuguese', name: 'Português', flag: '🇵🇹' },
    { code: 'Russian', name: 'Русский', flag: '🇷🇺' },
    { code: 'Arabic', name: 'العربية', flag: '🇸🇦' },
  ];

  return (
    <div className="w-full">
      <label htmlFor="language" className="block text-sm font-medium text-gray-700 mb-2">
        Summary Language
      </label>
      <select
        id="language"
        value={selectedLanguage}
        onChange={(e) => onLanguageChange(e.target.value)}
        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white text-gray-900"
      >
        {languages.map((lang) => (
          <option key={lang.code} value={lang.code}>
            {lang.flag} {lang.name}
          </option>
        ))}
      </select>
      <p className="mt-1 text-sm text-gray-500">
        The summary will be generated in {selectedLanguage}
      </p>
    </div>
  );
}
