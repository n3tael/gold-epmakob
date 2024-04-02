function enable_auto_load() {
    const galleryRect = document.querySelector('#gallery').getBoundingClientRect();

    if (currentPage == totalPages || totalPages == 0) {
        document.querySelector('p#loading').classList.add('hide');
    } else {
        document.querySelector('p#loading').classList.remove('hide');
    }

    if (window.innerHeight >= galleryRect.bottom) {
        load_posts();
    }
}

function load_posts() {
    const gallery = document.querySelector('#gallery');
    const galleryRect = gallery.getBoundingClientRect();
    const loading_text = document.querySelector('p#loading');

    if (currentPage != totalPages && totalPages != 0) {
        loading_text.classList.remove('hide');

        const request = new XMLHttpRequest();
        let url = document.URL.replace(/page=[0-9]+/,'page=' + (currentPage + 1));

        request.responseType = 'document';
        request.onload = (e) => {
            loading_text.classList.add('hide');

            let response = request.response;
            if (response.body) {
                let section = response.body.firstChild;

                gallery.appendChild(section);
                window.history.replaceState({}, null, url);
            }

            if (window.innerHeight >= galleryRect.bottom) {
                load_posts();
            }
        };

        request.open('GET', url);
        request.setRequestHeader('X-Requested-With', 'XMLHttpRequest');

        request.send();

        currentPage++;
    }
}

function scroll() {
    if ((window.innerHeight + window.scrollY) >= document.body.scrollHeight) {
        load_posts();
    }
}

document.addEventListener('DOMContentLoaded', enable_auto_load);
document.addEventListener('scroll', scroll);