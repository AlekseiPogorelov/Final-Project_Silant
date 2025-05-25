document.addEventListener('DOMContentLoaded', function() {
    var topScrollbar = document.querySelector('.top-scrollbar');
    var topScrollbarInner = topScrollbar.querySelector('div');
    var tableContainer = document.querySelector('.table-scrollbar-container');
    var table = tableContainer.querySelector('table');

    function syncScroll() {
        topScrollbar.scrollLeft = tableContainer.scrollLeft;
    }
    function syncScrollTop() {
        tableContainer.scrollLeft = topScrollbar.scrollLeft;
    }
    function updateWidth() {
        topScrollbarInner.style.width = table.scrollWidth + 'px';
    }

    // Синхронизация скроллов
    topScrollbar.addEventListener('scroll', syncScrollTop);
    tableContainer.addEventListener('scroll', syncScroll);

    // При изменении размеров — обновлять ширину
    window.addEventListener('resize', updateWidth);

    // Первичная установка ширины
    updateWidth();
});