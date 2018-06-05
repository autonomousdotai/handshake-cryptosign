
import { Observable } from 'rxjs';
import { Response, Request, NextFunction, Router } from 'express';
import * as moment  from 'moment';
import { isValid } from 'validator.lib';
import { save, createReportTnx } from '../models/report.store';
import { ReportRequest } from '../payloads/report.payload';

const router = Router({ mergeParams: true });

router.post('/add', (req: Request, res: Response, next: NextFunction) => {
  Observable
  .of(Object.assign({
    offchain: `_${+moment.utc()}`
  }, req.body))
  .flatMap(body => isValid(new ReportRequest(body)))
  .map(iReport => iReport.toRequestModel())
  .flatMap(iReport => createReportTnx(iReport))
  .flatMap(iReport => save(iReport))
  .subscribe(result => res.json(result), next);
});
export let report = router;
