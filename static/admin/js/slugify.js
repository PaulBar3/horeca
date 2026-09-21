(function() {
    'use strict';

    var map = {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e',
        'ё': 'yo', 'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k',
        'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r',
        'с': 's', 'т': 't', 'у': 'u', 'ф': 'f', 'х': 'kh', 'ц': 'ts',
        'ч': 'ch', 'ш': 'sh', 'щ': 'shch', 'ъ': '', 'ы': 'y', 'ь': '',
        'э': 'e', 'ю': 'yu', 'я': 'ya'
    };

    function transliterate(str) {
        return str.split('').map(function(ch) {
            var lower = ch.toLowerCase();
            var result = map[lower] !== undefined ? map[lower] : ch;
            if (lower !== ch && result) {
                result = result.charAt(0).toUpperCase() + result.slice(1);
            }
            return result;
        }).join('');
    }

    function slugify(text) {
        return transliterate(text)
            .toLowerCase()
            .replace(/[^a-z0-9]+/g, '-')
            .replace(/^-+|-+$/g, '');
    }

    function init() {
        var nameInputs = document.querySelectorAll('#id_name, #id_title');
        var slugInput = document.getElementById('id_slug');

        if (!slugInput || !nameInputs.length) return;

        nameInputs.forEach(function(input) {
            input.addEventListener('input', function() {
                slugInput.value = slugify(this.value);
            });
        });
    }

    // Try both DOMContentLoaded and immediate init
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
