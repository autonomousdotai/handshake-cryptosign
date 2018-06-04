
import { IReportRequest } from './report.type';
import { IsNumber } from 'class-validator';


export class ReportRequest {

    @IsNumber({ message: 'hid.must_number' })
    private hid: number;

    @IsNumber({ message: 'outcome.must_number' })
    private outcome: number;

    private offchain: string;

    constructor(body: any) {
        this.hid = body.hid;
        this.outcome = body.outcome;
        this.offchain = body.offchain;
    }

    toRequestModel(): IReportRequest {
        return {
            hid: this.hid,
            outcome: this.outcome,
            offchain: this.offchain
        };
    }
}
