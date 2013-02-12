function embed(url) {
    $.append('<object width="340" height="275"><param name="movie" value=""><param name="allowFullScreen" value="true"><embed src="" type="application/x-shockwave-flash" allowfullscreen="true" width="340" height="275"></object>');
}

$('a.embed').on('click', function(e) {
    var parent = $(this).parent();
    var url = $(this).data('url');
    $(this).remove();
    parent.append('<object width="340" height="275"><param name="movie" value="' + url + '"><param name="allowFullScreen" value="true"><embed src="' + url + '" type="application/x-shockwave-flash" allowfullscreen="true" width="340" height="275"></object>');
});
