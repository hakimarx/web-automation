/*
Author: Kevin Kurnia Wikarta
Version: 1.0.0
Website: https://kevkw.id/
Contact: kevkw.work@gmail.com
File: Js Utilities
*/

// Generate Datatable
function generateDataTable(tableId, url, options, dom = "<Bf<t>lip>") {
  let table = $("#" + tableId).DataTable({
    dom: dom,
    processing: true,
    serverSide: true,
    orderCellsTop: true,
    fixedHeader: true,
    ordering: false,
    autoWidth: false,
    bInfo: false,
    search: { return: true },
    ajax: {
      url: url,
      type: "POST",
      data: function (d) {
        return { ...d };
      },
    },
    columns: options.columns,
    buttons: options.buttons,
    drawCallback: function () {
      updateFooter(tableId);
    },
  });

  table.on("preXhr.dt", function () {
    showLoading();
  });

  table.on("xhr.dt", function () {
    hideLoading();
  });

  table.on("processing.dt", function (e, settings, processing) {
    processing ? showLoading() : hideLoading();
  });
}

function updateFooter(tableId) {
  let table = $("#" + tableId).DataTable();
  let pageInfo = table.page.info();

  let totalPages = Math.ceil(pageInfo.recordsDisplay / pageInfo.length);
  let paginationHtml = createPaginationHtml(pageInfo.page, totalPages);

  // Cleanup default pagination
  $("#" + tableId + "_length").remove();
  $("#" + tableId + "_paginate").remove();

  // Update custom pagination and showing entries
  $("#dt-pagination").html(paginationHtml);

  let showingText;

  if (pageInfo.recordsDisplay === 0) {
    showingText = `${pageInfo.start} - ${pageInfo.end} dari ${pageInfo.recordsDisplay}`;
  } else {
    showingText = `${pageInfo.start + 1} - ${pageInfo.end} dari ${
      pageInfo.recordsDisplay
    }`;
  }

  $("#dt-showing-entries").text(showingText);

  // Attach new pagination event
  attachPaginationEvents(tableId);
}

function createPaginationHtml(currentPage, totalPages) {
  let paginationHtml = '<ul class="pagination">';

  paginationHtml += `<li class="page-item ${
    currentPage === 0 ? "disabled" : ""
  }" data-page="${currentPage - 1}">
      <a class="page-link">&laquo;</a>
  </li>`;

  paginationHtml += `<li class="page-item ${
    currentPage >= totalPages - 1 ? "disabled" : ""
  }" data-page="${currentPage + 1}">
      <a class="page-link">&raquo;</a>
  </li>`;

  paginationHtml += "</ul>";
  return paginationHtml;
}

function attachPaginationEvents(tableId) {
  const table = $("#" + tableId).DataTable();

  $("#dt-pagination .page-item").on("click", function () {
    if ($(this).hasClass("disabled")) return;
    const page = $(this).data("page");
    table.page(page).draw("page");
  });

  $("#dt-entries-select").on("change", function () {
    const newLength = $(this).val();
    table.page.len(newLength).draw();
  });
}

// Handle Ketika foreign key
function delete_data(name, url, token, tableId) {
  Swal.fire({
    title: "Apakah anda yakin?",
    text: "Anda akan menghapus " + name + ".",
    icon: "warning",
    showCancelButton: true,
    confirmButtonColor: "#405189",
    cancelButtonColor: "#f06548",
    confirmButtonText: "Delete",
    cancelButtonText: "Cancel",
  }).then((result) => {
    if (result.isConfirmed) {
      $.ajax({
        url: url,
        type: "POST",
        data: {
          _token: token,
        },
        success: function (response) {
          showAlert("Terhapus!", name + " telah dihapus.", "success");

          $("#" + tableId)
            .DataTable()
            .ajax.reload(null, false);
        },
        error: function (xhr, status, error) {
          showAlert(
            "Error!",
            "Terjadi kesalahan ketika menghapus data.",
            "error"
          );
        },
      });
    }
  });
}

function getSelect2Value(element, url, selectedValue = "") {
  // Clear current options and set to loading
  $(element)
    .empty()
    .append(new Option("Loading...", "", true, true))
    .trigger("change");

  // Fetch data from the provided URL
  $.ajax({
    url: url,
    type: "GET",
    dataType: "json",
    success: function (data) {
      // Clear the loading option
      $(element).empty();

      // Add a placeholder option
      $(element).append(new Option("Please select...", "", true, false));

      // Populate the dropdown with new options
      $.each(data, function (index, item) {
        let isSelected = selectedValue && selectedValue == item.id;
        $(element).append(
          new Option(item.text, item.id, isSelected, isSelected)
        );
      });

      // Trigger change event for Select2 initialization
      $(element).trigger("change");
    },
    error: function () {
      // Handle errors and reset the dropdown
      $(element)
        .empty()
        .append(new Option("Error loading data", "", true, false))
        .trigger("change");
    },
  });
}

function showAlert(title, message, status = "error") {
  Swal.fire({
    position: "center",
    icon: status,
    title: title,
    text: message,
    showConfirmButton: false,
    timer: 3000,
  });
}

function getToast() {
  let toastStatus = sessionStorage.getItem("toastStatus");
  let toastMessage = sessionStorage.getItem("toastMessage");

  if (toastStatus && toastMessage) {
    return {
      status: toastStatus,
      message: toastMessage,
    };
  } else {
    return false;
  }
}

function setToast(status = "success", message) {
  sessionStorage.setItem("toastStatus", status);
  sessionStorage.setItem("toastMessage", message);
}

function removeToast() {
  sessionStorage.removeItem("toastStatus");
  sessionStorage.removeItem("toastMessage");
}

function showToast(status = "success", message) {
  let responseMessage;
  let backgroundStyle;

  switch (status) {
    case "success":
      responseMessage = `<i class="ri-checkbox-circle-line fs-5 align-middle"></i> <span class="fs-6 align-middle">${message}</span>`;
      backgroundStyle = "#0ab39c";
      break;
    case "error":
      responseMessage = `<i class="ri-close-circle-line fs-5 align-middle"></i> <span class="fs-6 align-middle">${message}</span>`;
      backgroundStyle = "#f06548";
      break;
    default:
      responseMessage = `<i class="ri-information-line fs-5 align-middle"></i> <span class="fs-6 align-middle">${message}</span>`;
      backgroundStyle = "#f7b84b";
  }

  Toastify({
    text: responseMessage,
    duration: 5000,
    newWindow: true,
    close: true,
    gravity: "top",
    position: "right",
    stopOnFocus: true,
    escapeMarkup: false,
    style: {
      background: backgroundStyle,
    },
  }).showToast();
}

function redirect(url, type) {
  if (typeof type === "undefined") type = "_self";

  window.open(url, type);
}

function booleanInteger(value, trueValue = "Ya", falseValue = "Tidak") {
  return value === "1" ? trueValue : falseValue;
}

function showIcon(iconName, sizeClass = "fs-2") {
  return `<i class="${iconName} ${sizeClass}"></i>`;
}

function verifiedLabel(status) {
  if (status === "0") {
    return `<span class="badge bg-warning"><i class="ri-refresh-line fs-17 align-middle"></i> Menunggu Verifikasi</span>`;
  } else if (status === "1") {
    return `<span class="badge bg-success"><i class="ri-checkbox-circle-line fs-17 align-middle"></i> Diterima</span>`;
  } else {
    return `<span class="badge bg-danger"><i class="ri-close-circle-line fs-17 align-middle"></i> Ditolak</span>`;
  }
}

function leaveVerifiedLabel(status) {
  if (status === "0") {
    return `<span class="badge bg-warning"><i class="ri-refresh-line fs-17 align-middle"></i> Menunggu Verifikasi</span>`;
  } else if (status === "1") {
    return `<span class="badge bg-success"><i class="ri-checkbox-circle-line fs-17 align-middle"></i> Diterima</span>`;
  } else if (status === "3") {
    return `<span class="badge bg-danger"><i class="ri-close-circle-line fs-17 align-middle"></i> Dibatalkan</span>`;
  } else {
    return `<span class="badge bg-danger"><i class="ri-close-circle-line fs-17 align-middle"></i> Ditolak</span>`;
  }
}

function taperaVerifiedLabel(status) {
  if (status === "0") {
    return `<span class="badge bg-warning"><i class="ri-refresh-line fs-17 align-middle"></i> Menunggu Verifikasi</span>`;
  } else if (status === "1") {
    return `<span class="badge bg-danger"><i class="ri-close-circle-line fs-17 align-middle"></i> Perbaikan Data</span>`;
  } else if (status === "2") {
    return `<span class="badge bg-success"><i class="ri-checkbox-circle-line fs-17 align-middle"></i> Pengajuan Ke Tapera</span>`;
  } else if (status === "3") {
    return `<span class="badge bg-success"><i class="ri-checkbox-circle-line fs-17 align-middle"></i> Diterima</span>`;
  } else {
    return `<span class="badge bg-danger"><i class="ri-close-circle-line fs-17 align-middle"></i> Ditolak</span>`;
  }
}

function presenceStatusLabel(status) {
  if (status === "presence") {
    return `<span class="badge bg-success"> Hadir </span>`;
  } else if (status === "office_travel_full") {
    return `<span class="badge bg-secondary">Dinas Luar Full </span>`;
  } else if (status === "office_travel_half") {
    return `<span class="badge bg-secondary">Dinas Luar Half </span>`;
  } else if (status === "leave") {
    return `<span class="badge bg-primary">Cuti </span>`;
  } else if (status === "late") {
    return `<span class="badge bg-warning">Terlambat </span>`;
  } else if (status === "rejected") {
    return `<span class="badge bg-danger">Ditolak </span>`;
  } else {
    return `<span class="badge bg-danger"> Absen </span>`;
  }
}

function detailButton(id, data, ...params) {
  // Delete null or undefined parameter
  let filteredParams = params.filter(
    (param) => param !== null && param !== undefined
  );

  // If params exists, seperate with "/"
  let paramString = filteredParams.length ? filteredParams.join("/") + "/" : "";

  return `<a href="${
    site_url + uri_name + "/detail/" + paramString + id
  }" class="fw-bold">${data}</a>`;
}

function handleDropdownChange(
  dependentSelector,
  triggerSelector,
  apiUrl,
  selectedValue = ""
) {
  function updateDropdown() {
    let value = $(dependentSelector).val();

    if (value !== "") {
      let url = apiUrl + value;
      $(triggerSelector).prop("disabled", false);

      getSelect2Value(triggerSelector, url, selectedValue);
    } else {
      $(triggerSelector).val("").trigger("change");
      $(triggerSelector).prop("disabled", true);
    }
  }

  // Initialize on page load
  updateDropdown();

  // Add on change event listener
  $(dependentSelector).on("change", updateDropdown);
}

function initDownloadButton(selector, url, fileName) {
  $("#" + selector).on("click", function (e) {
    e.preventDefault();

    $.ajax({
      url: url,
      method: "GET",
      xhrFields: {
        responseType: "blob",
      },
      success: function (data, status, xhr) {
        let blob = new Blob([data], {
          type: xhr.getResponseHeader("Content-Type"),
        });

        let url = window.URL.createObjectURL(blob);

        let a = document.createElement("a");
        a.href = url;
        a.download = fileName;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);

        showToast("success", "File Berhasil Diunduh!");
      },
      error: function (err) {
        console.log(err);
        showAlert(
          "Error!",
          err.responseJSON?.message || "File Tidak Ditemukan!",
          err.responseJSON?.status || "error"
        );
      },
    });
  });
}

function initTableDownloadButton(selector, url) {
  $(document)
    .off("click", "#" + selector)
    .on("click", "#" + selector, function (e) {
      e.preventDefault();

      let fileName = $(this).data("file-name");
      let employeeNumber = $(this).data("employee-number");
      let decodedUrl = decodeURIComponent(url);

      let newUrl = decodedUrl;
      if (decodedUrl.includes("{employee_number}")) {
        newUrl = decodedUrl.replace("{employee_number}", employeeNumber);
      }

      newUrl += fileName;

      $.ajax({
        url: newUrl,
        method: "GET",
        xhrFields: {
          responseType: "blob",
        },
        success: function (data, status, xhr) {
          var blob = new Blob([data], {
            type: xhr.getResponseHeader("Content-Type"),
          });

          var url = window.URL.createObjectURL(blob);
          var a = document.createElement("a");
          a.href = url;
          a.download = fileName;
          document.body.appendChild(a);
          a.click();
          document.body.removeChild(a);
          window.URL.revokeObjectURL(url);

          showToast("success", "File Berhasil Diunduh!");
        },
        error: function (err) {
          console.log(err);
          showAlert(
            "Error!",
            err.responseJSON?.message || "File Tidak Ditemukan!",
            err.responseJSON?.status || "error"
          );
        },
      });
    });
}

function initAjaxSelect2(selector, url, selectedId = null, method = "GET") {
  const $el = $("#" + selector);

  $el.select2({
    placeholder: "- Silahkan Pilih -",
    allowClear: true,
    width: "100%",
    ajax: {
      url: url,
      dataType: "json",
      delay: 250,
      data: function (params) {
        return {
          q: params.term,
        };
      },
      processResults: function (data) {
        return {
          results: data,
        };
      },
      cache: true,
    },
    minimumInputLength: 2,
  });

  // If selected id is not null
  if (selectedId) {
    $.ajax({
      type: method,
      url: url,
      data: { id: selectedId },
    }).then(function (data) {
      const option = new Option(data.text, data.id, true, true);
      $el.append(option).trigger("change");
      $el.trigger({
        type: "select2:select",
        params: {
          data: data,
        },
      });
    });
  }
}

function initAjaxSelect2Multiple(elementId, ajaxUrl, selectedIds = []) {
  let $select = $("#" + elementId);

  $select.select2({
    ajax: {
      url: ajaxUrl,
      type: "POST",
      dataType: "json",
      delay: 250,
      data: function (params) {
        return {
          q: params.term, // search term
          page: params.page || 1,
        };
      },
      processResults: function (data, params) {
        params.page = params.page || 1;

        return {
          results: data.results,
          pagination: {
            more: data.more || false,
          },
        };
      },
      cache: true,
    },
    placeholder: "Pilih Pegawai...",
    minimumInputLength: 2,
    multiple: true,
    allowClear: true,
  });

  if (selectedIds.length > 0) {
    $.ajax({
      url: ajaxUrl,
      type: "POST",
      dataType: "json",
      data: {
        ids: selectedIds,
      },
      success: function (data) {
        if (data.results && data.results.length > 0) {
          $.each(data.results, function (index, item) {
            let option = new Option(item.text, item.id, true, true);
            $select.append(option).trigger("change");
          });
        }
      },
      error: function (xhr, status, error) {
        console.error("Error loading selected data:", error);
      },
    });
  }
}

function formatDate(dateStr, showDay = true) {
  const days = ["Minggu", "Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu"];

  const months = [
    "",
    "Januari",
    "Februari",
    "Maret",
    "April",
    "Mei",
    "Juni",
    "Juli",
    "Agustus",
    "September",
    "Oktober",
    "November",
    "Desember",
  ];

  if (!dateStr || dateStr.length !== 10) {
    return "Invalid Date Type";
  }

  const year = parseInt(dateStr.substring(0, 4));
  const monthNum = parseInt(dateStr.substring(5, 7));
  const dayNum = parseInt(dateStr.substring(8, 10));

  const dateObj = new Date(year, monthNum - 1, dayNum);
  if (
    dateObj.getFullYear() !== year ||
    dateObj.getMonth() + 1 !== monthNum ||
    dateObj.getDate() !== dayNum
  ) {
    return "Invalid Date Format";
  }

  let text = "";
  if (showDay) {
    const dayName = days[dateObj.getDay()];
    text = `${dayName}, ${dayNum} ${months[monthNum]} ${year}`;
  } else {
    text = `${dayNum} ${months[monthNum]} ${year}`;
  }

  return text;
}

function initFormRepeater(
  templateId,
  wrapperSelector,
  afterAppendCallback,
  data = {},
  prefix = null
) {
  const $template = $("#" + templateId);

  if ($template.length === 0) return;

  const $clone = $($template.html()); // Get template as jQuery object
  const $newElement = $clone.filter(".repeater-item"); // Get element with repeater-item class

  // Inject data jika ada
  if (data && typeof data === "object") {
    for (const key in data) {
      if (data.hasOwnProperty(key)) {
        let $input = $newElement.find(`[name="${key}[]"]`);

        if (prefix != null) {
          $input = $newElement.find(`[name="${prefix + key}[]"]`);
        }

        if ($input.length > 0) {
          if ($input.is("select")) {
            // Select existing options
            const val = data[key];
            $input.val(val).trigger("change");
          } else {
            $input.val(data[key]);
          }
        }
      }
    }
  }

  $(wrapperSelector).append($newElement);

  // Init Select2 jika ada
  $newElement.find("select.select2").select2();

  // Callback setelah append
  if (typeof afterAppendCallback === "function") {
    afterAppendCallback();
  }
}