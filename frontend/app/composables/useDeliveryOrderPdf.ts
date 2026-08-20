import angkaTerbilang from "@develoka/angka-terbilang-js";
import { useChangeCase } from "@vueuse/integrations/useChangeCase.js";
import logoImage from "~/assets/images/map-logo-only.jpg";
import type { Details } from "~/types/operations";

/**
 * Bangun PDF Surat Pengantar Pengiriman (Delivery Order) dari data details.
 * Dipakai oleh halaman detail (surat) maupun preview sebelum simpan.
 */
export function useDeliveryOrderPdf() {
  const { user } = useAuth();

  async function buildDeliveryOrderPdf(
    details: Details,
  ): Promise<string | null> {
    const pdfMake = usePDFMake();
    if (!pdfMake || import.meta.server) return null;

    const surat = details;
    const tableBodyNotes: {
      text: string;
      border: [boolean, boolean, boolean, boolean];
    }[][] = [
      [
        {
          text: "Catatan :",
          border: [true, false, true, false],
        },
      ],
    ];

    let i = 1;
    for (const note of surat.notes || []) {
      tableBodyNotes.push([
        {
          text: `${i++}. ${note.note || ""}` || "",
          border: [true, false, true, false],
        },
      ]);
    }

    return await pdfMake
      .createPdf({
        info: {
          title: `Delivery Order ${surat.doInformation?.doNumber || ""}`,
          author: "PT. Mitra Andalan Petroleum",
          creator: user.value?.name,
          producer: "PT. Mitra Andalan Petroleum",
        },
        pageMargins: [24, 24, 24, 24],
        pageSize: "A4",
        content: [
          {
            layout: {
              paddingRight: function () {
                return 10;
              },
              paddingLeft: function () {
                return 10;
              },
              paddingBottom: function () {
                return 10;
              },
              paddingTop: function () {
                return 10;
              },
              fillColor: function () {
                return null;
              },
            },
            table: {
              widths: ["25%", "*"],
              body: [
                [
                  {
                    image: await toBase64(logoImage),
                    width: 30,
                    alignment: "center",
                    border: [true, true, false, false],
                  },
                  {
                    text: "SURAT PENGANTAR PENGIRIMAN (DELIVERY ORDER)",
                    bold: true,
                    fontSize: 11,
                    border: [false, true, true, false],
                  },
                ],
              ],
            },
          },
          {
            layout: {
              defaultBorder: false,
              paddingRight: function () {
                return 2;
              },
              paddingLeft: function () {
                return 2;
              },
              paddingBottom: function () {
                return 1;
              },
              paddingTop: function () {
                return 1;
              },
              fillColor: function () {
                return null;
              },
            },
            table: {
              widths: ["*", "15%", "auto", "30%"],
              body: [
                [
                  {
                    text: `${surat.companyInformation.name}`,
                    bold: true,
                    border: [true, false, false, false],
                  },
                  { text: "" },
                  { text: "" },
                  {
                    text: "",
                    border: [false, false, true, false],
                  },
                ],
                [
                  {
                    text: `${surat.companyInformation.nameSub}`,
                    italics: true,
                    border: [true, false, false, false],
                  },
                  {
                    text: "No. DO MAP",
                    bold: true,
                  },
                  {
                    text: ":",
                  },
                  {
                    text: `${surat.doInformation.doNumber}`,
                    border: [false, false, true, false],
                  },
                ],
                [
                  {
                    text: `${surat.companyInformation.address}`,
                    border: [true, false, false, false],
                  },
                  {
                    text: "Tgl. DO",
                    bold: true,
                  },
                  {
                    text: ":",
                  },
                  {
                    text: formatDateDoc(surat.doInformation.doDateCreated),
                    border: [false, false, true, false],
                  },
                ],
                [
                  {
                    text: `${surat.companyInformation.phoneNumber}`,
                    border: [true, false, false, false],
                  },
                  {},
                  {
                    text: ":",
                  },
                  {
                    text: "",
                    border: [false, false, true, false],
                  },
                ],
                [
                  {
                    text: "",
                    border: [true, false, false, false],
                  },
                  {
                    text: "NO. PO Cust.",
                    bold: true,
                  },
                  {
                    text: ":",
                  },
                  {
                    text: `${surat.doInformation.poCustomerNumber.purchaseOrderNumber}`,
                    border: [false, false, true, false],
                  },
                ],
                [
                  {
                    text: "",
                    border: [true, false, false, false],
                  },
                  {
                    text: "No. SO",
                    bold: true,
                  },
                  {
                    text: ":",
                  },
                  {
                    text: `${surat.doInformation.soNumber || ""}\n\n`,
                    border: [false, false, true, false],
                  },
                ],
              ],
            },
          },
          {
            layout: {
              defaultBorder: false,
              paddingRight: function () {
                return 2;
              },
              paddingLeft: function () {
                return 2;
              },
              paddingBottom: function () {
                return 2;
              },
              paddingTop: function () {
                return 2;
              },
              fillColor: function () {
                return null;
              },
            },
            table: {
              widths: ["auto", "auto", "*", "auto", "auto", "*"],
              body: [
                [
                  {
                    text: "Diserahkan Kepada",
                    bold: true,
                    border: [true, true, false, false],
                  },
                  {
                    text: ":",
                    border: [false, true, false, false],
                  },
                  {
                    text: `${surat.customerName}`,
                    border: [false, true, false, false],
                  },
                  {
                    text: "Agen/ Transportir",
                    bold: true,
                    border: [true, true, false, false],
                  },
                  {
                    text: ":",
                    border: [false, true, false, false],
                  },
                  {
                    text: `${surat.transportName}\n\n\n`,
                    border: [false, true, true, false],
                  },
                ],
                [
                  {
                    text: "ID. Pelanggan",
                    bold: true,
                    border: [true, false, false, false],
                  },
                  {
                    text: ":",
                  },
                  {
                    text: `${surat.customerName}`,
                  },
                  {
                    text: "ID",
                    bold: true,
                    border: [true, false, false, false],
                  },
                  {
                    text: ":",
                  },
                  {
                    text: `${surat.transportId || ""}`,
                    border: [false, false, true, false],
                  },
                ],
                [
                  {
                    text: "Alamat",
                    bold: true,
                    border: [true, false, false, false],
                  },
                  {
                    text: ":",
                  },
                  {
                    text: `${surat.customerAddress || ""}`,
                    border: [false, false, true, false],
                  },
                  {
                    text: "Alamat",
                    bold: true,
                    border: [true, false, false, false],
                  },
                  {
                    text: ":",
                  },
                  {
                    text: `${surat.transportAddress || ""}\n\n\n`,
                    border: [false, false, true, false],
                  },
                ],
                [
                  {
                    text: "Penerima BBM+HP",
                    bold: true,
                    border: [true, false, false, false],
                  },
                  {
                    text: ":",
                  },
                  {
                    text: `${surat.receiverInformation.name || ""}`,
                  },
                  {
                    text: "Driver + HP",
                    bold: true,
                    border: [true, false, false, false],
                  },
                  {
                    text: ":",
                  },
                  {
                    text: `${surat.driverInformation.name || ""} ${surat.driverInformation.phoneNumber ? "-" : ""} ${surat.driverInformation.phoneNumber || ""}\n\n\n`,
                    border: [false, false, true, false],
                  },
                ],
                [
                  {
                    text: "",
                    border: [true, false, false, false],
                  },
                  { text: "" },
                  { text: "" },
                  {
                    text: "Kenet/Helper",
                    bold: true,
                    border: [true, false, false, false],
                  },
                  {
                    text: ":",
                  },
                  {
                    text: `${surat.helperName || ""}`,
                    border: [false, false, true, false],
                  },
                ],
                [
                  {
                    text: "Tanggal",
                    bold: true,
                    border: [true, false, false, false],
                  },
                  {
                    text: ":",
                  },
                  {
                    text:
                      surat.receiverDateReceived === undefined
                        ? formatDateDoc(surat.receiverDateReceived)
                        : "",
                    border: [false, false, true, false],
                  },
                  {
                    text: "Tanggal",
                    bold: true,
                    border: [true, false, false, false],
                  },
                  {
                    text: ":",
                  },
                  {
                    text:
                      surat.receiverDateReceived === undefined
                        ? formatDateDoc(surat.transportDateReceived)
                        : "",
                    border: [false, false, true, false],
                  },
                ],
              ],
            },
          },
          {
            layout: {
              paddingRight: function () {
                return 2;
              },
              paddingLeft: function () {
                return 2;
              },
              paddingBottom: function () {
                return 2;
              },
              paddingTop: function () {
                return 2;
              },
              fillColor: function () {
                return null;
              },
            },
            table: {
              widths: ["*", "*", "*", "*", "*", "*"],
              body: [
                [
                  {
                    text: "Tanggal Berlaku",
                    alignment: "center",
                    bold: true,
                    colSpan: 2,
                  },
                  {},
                  {
                    text: "Produk",
                    alignment: "center",
                    bold: true,
                    colSpan: 2,
                  },
                  {},
                  {
                    text: "Volume/ Kuantitas (Liter)",
                    alignment: "center",
                    bold: true,
                    colSpan: 2,
                  },
                  {},
                ],
                [
                  {
                    text: `${surat.dueDate !== undefined ? formatDateDoc(surat.dueDate) : ""}`,
                    colSpan: 2,
                    alignment: "center",
                  },
                  {},
                  {
                    text: `${surat.productInformation.name || ""}`,
                    colSpan: 2,
                    alignment: "center",
                  },
                  {},
                  {
                    text: `${formatNumber(surat.productInformation.qty || 0)} Liter`,
                    colSpan: 2,
                    alignment: "center",
                  },
                  {},
                ],
                [
                  {
                    text: "Dikirim Dengan",
                    bold: true,
                  },
                  {},
                  {
                    text: "Segel Atas",
                    rowSpan: 2,
                    verticalAlignment: "middle",
                    bold: true,
                  },
                  {
                    text: `${surat.productInformation.topSeal || ""}`,
                    rowSpan: 2,
                    verticalAlignment: "middle",
                    alignment: "center",
                  },
                  {
                    text: "Bebas Air",
                    bold: true,
                  },
                  {
                    text: "Ya / Tidak",
                    alignment: "center",
                  },
                ],
                [
                  {
                    text: "No. Kendaraan",
                    bold: true,
                  },
                  {
                    text: `${surat.transportInformation.transportNumber || ""}`,
                  },
                  { text: "" },
                  { text: "" },
                  {
                    text: "Jam Berangkat",
                    bold: true,
                  },
                  {
                    text: `${surat.transportInformation.timeInformation.departureTime || ""}`,
                  },
                ],
                [
                  {
                    text: "Km. Awal",
                    bold: true,
                  },
                  {
                    text: `${surat.transportInformation.startKm || ""}`,
                  },
                  {
                    text: "Segel Bawah",
                    rowSpan: 2,
                    verticalAlignment: "middle",
                    bold: true,
                  },
                  {
                    text: `${surat.productInformation.bottomSeal || ""}`,
                    rowSpan: 2,
                    verticalAlignment: "middle",
                    alignment: "center",
                  },
                  {
                    text: "Jam Tiba",
                    bold: true,
                  },
                  {
                    text: `${surat.transportInformation.timeInformation.arrivalTime || ""}`,
                  },
                ],
                [
                  {
                    text: "Km. Akhir",
                    bold: true,
                  },
                  {
                    text: `${surat.transportInformation.endKm || ""}`,
                  },
                  { text: "" },
                  { text: "" },
                  {
                    text: "Jam Mulai Pembongkaran",
                    bold: true,
                  },
                  {
                    text: `${surat.transportInformation.timeInformation.unloadingTime || ""}`,
                  },
                ],
                [
                  {
                    text: "SG Meter",
                    bold: true,
                  },
                  {
                    text: `${surat.transportInformation.sgMeter || ""}`,
                  },
                  {
                    text: "Temperatur",
                    bold: true,
                  },
                  {
                    text: `${surat.productInformation.temperature || ""}`,
                  },
                  {
                    text: "Jam Tiba di Depo",
                    bold: true,
                  },
                  {
                    text: `${surat.transportInformation.timeInformation.depotArrivalTime || ""}`,
                  },
                ],
                [
                  { text: "", border: [true, true, false, true] },
                  { text: "", border: [false, true, false, true] },
                  { text: "", border: [false, true, false, true] },
                  { text: "", border: [false, true, false, true] },
                  { text: "", border: [false, true, false, true] },
                  { text: "", border: [false, true, true, true] },
                ],
                [
                  {
                    text: "Jumlah (Liter)",
                    bold: true,
                  },
                  {
                    text: `${formatNumber(surat.productInformation.qty || 0)} # (${useChangeCase(angkaTerbilang(surat.productInformation.qty), "capitalCase").value} Liter) #`,
                    italics: true,
                    colSpan: 5,
                  },
                  {},
                  {},
                  {},
                  {},
                ],
              ],
            },
          },
          {
            layout: {
              paddingRight: function () {
                return 100;
              },
              paddingLeft: function () {
                return 2;
              },
              paddingBottom: function (i, node) {
                return i === node.table.body.length - 1 ? 15 : 2;
              },
              paddingTop: function (i) {
                return i === 0 ? 15 : 2;
              },
              fillColor: function () {
                return null;
              },
            },
            table: {
              widths: ["*"],
              body: tableBodyNotes,
            },
          },
          {
            layout: {
              defaultBorder: false,
              paddingRight: function () {
                return 2;
              },
              paddingLeft: function () {
                return 2;
              },
              paddingBottom: function () {
                return 15;
              },
              paddingTop: function () {
                return 2;
              },
              fillColor: function () {
                return null;
              },
            },
            table: {
              widths: ["*", "auto", "*", "*", "auto", "*"],
              body: [
                [
                  {
                    text: "T2 DEPO",
                    bold: true,
                    border: [true, false, false, false],
                  },
                  {
                    text: ":",
                  },
                  {
                    text: "______________________",
                  },
                  {
                    text: "KEPEKAAN INDEX\n(buku tera mobil)",
                    bold: true,
                  },
                  {
                    text: ":",
                  },
                  {
                    text: "______________________",
                    border: [false, false, true, false],
                  },
                ],
                [
                  {
                    text: "T2 BONGKAR",
                    bold: true,
                    border: [true, false, false, false],
                  },
                  {
                    text: ":",
                  },
                  {
                    text: "______________________",
                  },
                  {
                    text: "BBM DITERIMA",
                    bold: true,
                  },
                  {
                    text: ":",
                  },
                  {
                    text: "______________________ Liter",
                    border: [false, false, true, false],
                  },
                ],
              ],
            },
          },
          {
            layout: {
              paddingRight: function () {
                return 10;
              },
              paddingLeft: function () {
                return 10;
              },
              paddingBottom: function () {
                return 2;
              },
              paddingTop: function (i) {
                return i === 1 ? 75 : 2;
              },
              fillColor: function (i) {
                return i === 0 ? "#e5e5e5" : null;
              },
            },
            table: {
              widths: ["auto", "auto", "*", "*"],
              body: [
                [
                  {
                    text: "Koordinator MAP",
                    alignment: "center",
                    bold: true,
                  },
                  {
                    text: "Adm. Distribusi",
                    alignment: "center",
                    bold: true,
                  },
                  {
                    text: "Penerima",
                    alignment: "center",
                    bold: true,
                  },
                  {
                    text: "Driver/Officer",
                    alignment: "center",
                    bold: true,
                  },
                ],
                [
                  {
                    text: `${surat.companyCoordinator || ""}`,
                    alignment: "center",
                    bold: true,
                  },
                  {
                    text: `${surat.distributionAdmin || ""}`,
                    alignment: "center",
                    bold: true,
                  },
                  {
                    text: `${surat.receiver || ""}`,
                    alignment: "center",
                    bold: true,
                  },
                  {
                    text: `${surat.driver || ""}`,
                    alignment: "center",
                    bold: true,
                  },
                ],
                [
                  { text: "", border: [true, true, false, true] },
                  { text: "", border: [false, true, false, true] },
                  { text: "", border: [false, true, false, true] },
                  { text: "", border: [false, true, true, true] },
                ],
              ],
            },
          },
        ],
        defaultStyle: {
          color: "#000000",
          fontSize: 9,
        },
      })
      .getDataUrl();
  }

  return { buildDeliveryOrderPdf };
}
