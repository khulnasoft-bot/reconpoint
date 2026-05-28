function checkedCount() {
  // this function will count the number of boxes checked
  item = document.getElementsByClassName("subdomain_checkbox");
  count = 0;
  for (let i = 0; i < item.length; i++) {
    if (item[i].checked) {
      count++;
    }
  }
  
  // Dispatch event for Alpine.js
  window.dispatchEvent(new CustomEvent('subdomain-selection-change', { detail: { count: count } }));
  
  return count;
}

function mainCheckBoxSelected(checkbox) {
  if (checkbox.checked) {
    $("[data-button=subdomain_btns]").removeClass("disabled");
    $(".subdomain_checkbox").prop('checked', true);
    $('#subdomain_selected_count').text(checkedCount() + ' Subdomains Selected x');
  } else {
    uncheckSubdomains();
  }
}

function toggleMultipleSubdomainButton() {
  let checked_count = checkedCount();
  if (checked_count > 0) {
    $("[data-button=subdomain_btns]").removeClass("disabled");
    $('#subdomain_selected_count').text(checked_count + ' Subdomains Selected x');
  } else {
    $("[data-button=subdomain_btns]").addClass("disabled");
    $('#subdomain_selected_count').empty();
  }
}

function uncheckSubdomains(){
  $("[data-button=subdomain_btns]").addClass("disabled");
  $(".subdomain_checkbox").prop('checked', false);
  $("#head_checkbox").prop('checked', false);
  $('#subdomain_selected_count').empty();
  
  // Dispatch event for Alpine.js
  window.dispatchEvent(new CustomEvent('subdomain-selection-change', { detail: { count: 0 } }));
}

// Link custom search input to DataTable
$(document).ready(function() {
  $('#subdomain-table-filter').on('keyup', function() {
    var table = $('#subdomain_scan_results').DataTable();
    table.search(this.value).draw();
  });
});

