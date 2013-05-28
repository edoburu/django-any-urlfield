(function($)
{
  $(document).ready(function(){
    var widgets = $("ul.any_urlfield-url_type");

    if($.fn.on) {
      // jQuery 1.7+
      $('body').on('change', 'ul.any_urlfield-url_type input', onUrlTypeChange);
    }
    else {
      widgets.find("input").live('change', onUrlTypeChange);
    }

    // Apply by default
    widgets.each(function(){ updatePanels($(this)); });
  });


  function onUrlTypeChange(event)
  {
    var widget = $(this).parent().closest('.any_urlfield-url_type');
    updatePanels(widget);
  }

  function updatePanels(widget)
  {
    var inputs = widget.find('input');
    inputs.each(function(){
      var slugvalue = this.value.replace(/[^a-z0-9-_]/, '');
      var pane = widget.siblings(".any_urlfield-url-" + slugvalue);
      pane[ this.checked ? "show" : "hide" ]();
    });
  }

})(window.jQuery || window.django.jQuery);
