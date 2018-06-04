
export interface IReportRequest {
    hid: number;
    outcome: number;
    offchain: string;
}

export interface IReport {
    id: number;
    outcome: number;
    tnx_hash: string;
    offchain: string;
}
