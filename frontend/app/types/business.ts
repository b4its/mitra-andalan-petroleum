export interface ProductDOItem {
  name?: string
  qty?: number
  selected?: boolean
  delivered?: boolean
  delivered_at?: string
}

export interface DOProductInformation {
  name?: string
  qty?: number
  temperature?: number
  topSeal?: string
  bottomSeal?: string
}

export interface DOTimeInformation {
  departureTime?: string
  arrivalTime?: string
  unloadingTime?: string
  depotArrivalTime?: string
}

export interface DOTransportInformation {
  transportType?: string
  transportNumber?: string
  startKm?: number
  endKm?: number
  sgMeter?: number
  timeInformation?: DOTimeInformation
}
