public JsonResult AllocateItem(AllocationPostingModelList model)
        {
            try
            {

                var tempModel = model;
                _allocationServices.DistributeAllocation(tempModel);

                var PartAllocationListForDeposit = model.Deposits.Where(x => x.AmountOutstanding != x.AmountToAllocate).ToList();
                var PartAllocationListForWithDraw = model.Withdrawals.Where(x => x.AmountOutstanding != x.AmountToAllocate).ToList();
                model.Deposits.RemoveAll(x => x.AmountOutstanding != x.AmountToAllocate);
                model.Withdrawals.RemoveAll(x => x.AmountOutstanding != x.AmountToAllocate);
                PartAllocationListForDeposit.ForEach(x => x.isPartAllocated = (x.AmountOutstanding == x.AmountToAllocate) ? false : true);
                PartAllocationListForWithDraw.ForEach(x => x.isPartAllocated = (x.AmountOutstanding == x.AmountToAllocate) ? false : true);
                foreach (var item in PartAllocationListForDeposit)
                {
                    AllocationPostingModel allocationModel = new AllocationPostingModel();
                    allocationModel.AgainstAmount = item.AgainstAmount;
                    allocationModel.AmountDistributed = item.AmountDistributed;
                    allocationModel.AmountOutstanding = item.AmountOutstanding;
                    allocationModel.AmountToAllocate = item.AmountToAllocate;
                    allocationModel.isAllocated = item.isAllocated;
                    allocationModel.IsEdited = item.IsEdited;
                    allocationModel.ItemId = item.ItemId;
                    allocationModel.ItemType = item.ItemType;
                    allocationModel.isPartAllocated = item.isPartAllocated;
                    model.Deposits.Add(allocationModel);
                }
                foreach (var item in PartAllocationListForWithDraw)
                {
                    AllocationPostingModel allocationModel = new AllocationPostingModel();
                    allocationModel.AgainstAmount = item.AgainstAmount;
                    allocationModel.AmountDistributed = item.AmountDistributed;
                    allocationModel.AmountOutstanding = item.AmountOutstanding;
                    allocationModel.AmountToAllocate = item.AmountToAllocate;
                    allocationModel.isAllocated = item.isAllocated;
                    allocationModel.IsEdited = item.IsEdited;
                    allocationModel.ItemId = item.ItemId;
                    allocationModel.ItemType = item.ItemType;
                    allocationModel.isPartAllocated = item.isPartAllocated;
                    model.Withdrawals.Add(allocationModel);
                }
                model.Deposits.ForEach(x => x.isPartAllocated = (x.AmountOutstanding == x.AmountToAllocate) ? false : true);
                model.Withdrawals.ForEach(x => x.isPartAllocated = (x.AmountOutstanding == x.AmountToAllocate) ? false : true);
                int i = 0;
                int j = 0;
                #region AllocationCalculationWork
                while (i < model.Deposits.Count)
                {
                    while (model.Withdrawals[j].isAllocated == false)
                    {
                        if (model.Deposits[i].isAllocated == false && model.Withdrawals[j].isAllocated == false)
                        {
                            if (model.Deposits[i].AmountToAllocate > model.Withdrawals[j].AmountToAllocate)
                            {
                                model.Deposits[i].AmountDistributed = Math.Abs(model.Withdrawals[j].AmountToAllocate - model.Deposits[i].AmountToAllocate);
                                model.Deposits[i].isAllocated = false;
                                model.Deposits[i].AgainstAmount = model.Withdrawals[j].AmountToAllocate;
                                model.Withdrawals[j].isAllocated = model.Deposits[i].AmountToAllocate >= model.Withdrawals[j].AmountToAllocate ? true : false;
                                model.Withdrawals[j].IsEdited = true;
                                model.Deposits[i].IsEdited = true;
                                model.Deposits[i].AmountToAllocate = model.Deposits[i].AmountDistributed == 0 ? model.Deposits[i].AmountToAllocate : model.Deposits[i].AmountDistributed;
                            }
                            else
                            {
                                model.Withdrawals[j].AmountDistributed = Math.Abs(model.Withdrawals[j].AmountToAllocate - model.Deposits[i].AmountToAllocate);
                                model.Deposits[i].isAllocated = model.Deposits[i].AmountToAllocate <= model.Withdrawals[j].AmountToAllocate ? true : false;
                                model.Deposits[i].IsEdited = true;
                               
                                if (model.Withdrawals[j].AmountToAllocate >= model.Deposits[i].AmountToAllocate)
                                {
                                    model.Withdrawals[j].isAllocated = model.Withdrawals[j].AmountToAllocate > model.Deposits[i].AmountToAllocate ? false : true;
                                    model.Withdrawals[j].isAllocated = model.Withdrawals[j].AmountToAllocate == model.Deposits[i].AmountToAllocate ? true : model.Withdrawals[j].isAllocated;
                                    model.Withdrawals[j].IsEdited = true;
                                    model.Withdrawals[j].AmountToAllocate = model.Withdrawals[j].AmountDistributed == 0 ? model.Withdrawals[j].AmountToAllocate : model.Withdrawals[j].AmountDistributed;
                                }
                                else {
                                    model.Withdrawals[j].isAllocated = false;
                                    model.Withdrawals[j].IsEdited = model.Deposits[i].AmountToAllocate >= model.Withdrawals[j].AmountToAllocate;
                                }
                                model.Withdrawals[j].AgainstAmount = model.Deposits[i].AmountToAllocate;
                                if (model.Deposits[i].AmountToAllocate < model.Withdrawals[j].AmountToAllocate)
                                {
                                    model.Deposits[i].AgainstAmount = model.Withdrawals[j].AmountOutstanding - model.Withdrawals[j].AmountDistributed;
                                }
                                else
                                {
                                    model.Deposits[i].AgainstAmount = model.Withdrawals[j].AmountOutstanding != 0 ? model.Withdrawals[j].AmountOutstanding : model.Withdrawals[j].AmountToAllocate;
                                }
                            }

                        }
                        if (model.Withdrawals[j].isAllocated && j < model.Withdrawals.Count - 1)
                        {
                            j++;
                        }
                        else if (model.Deposits[i].isAllocated && i < model.Deposits.Count - 1)
                        {
                            i++;
                        }
                        else
                        {
                            break;
                        }
                    }
                    if (model.Deposits[i].isAllocated && i < model.Deposits.Count - 1)
                    {
                        i++;
                    }
                    if (model.Deposits.Count >= model.Withdrawals.Count)
                    {
                        var condition = model.Withdrawals.Where(x => x.isAllocated == true).Count() == model.Withdrawals.Count;
                        if (condition)
                        {
                            break;
                        }
                    }
                    if (model.Withdrawals.Count >= model.Deposits.Count)
                    {
                        var condition = model.Deposits.Where(x => x.isAllocated == true).Count() == model.Deposits.Count;
                        if (condition)
                        {
                            break;
                        }
                    }
                    if (model.Withdrawals.Count <= model.Deposits.Count)
                    {
                        var condition = model.Deposits.Where(x => x.isAllocated == true).Count() == model.Deposits.Count;
                        if (condition)
                        {
                            break;
                        }
                    }
                }
                #endregion
                #region updateOutstandingAmount
                model.Withdrawals = model.Withdrawals.Where(x => x.IsEdited == true).ToList();
                model.Deposits = model.Deposits.Where(x => x.IsEdited == true).ToList();
                var depositList = model.Deposits;
                var withdrawalList = model.Withdrawals;
                #region DepositUpdateOutstandingAmount
                if (depositList != null)
                {
                    foreach (var deposit in depositList)
                    {
                        if (deposit.ItemType == AllocationItem.BankTransactionDeposit)
                        {
                            var entity = _bankAccountTransactionServices.GetById(deposit.ItemId);
                            if (deposit.isAllocated && deposit.isPartAllocated == false)
                            {
                                entity.Allocated = Convert.ToString((Int64)BankAccountAllocateType.Allocated);
                                entity.AmountOutstanding = 0;
                            }
                            else
                            {
                                entity.Allocated = Convert.ToString((Int64)BankAccountAllocateType.PartAllocated);
                                entity.AmountOutstanding = deposit.isPartAllocated ? deposit.AmountOutstanding - deposit.AmountToAllocate : deposit.AmountToAllocate;
                            }

                            _bankAccountTransactionServices.SaveForAllocation(entity);
                        }
                        else if (deposit.ItemType == AllocationItem.CustomerCreditNote)
                        {
                            var entity = _creditNoteServices.GetById(deposit.ItemId);
                            if (deposit.isAllocated && deposit.isPartAllocated == false)
                            {
                                entity.CreditNoteStatus = Convert.ToString((Int64)CreditNoteStatus.Paid);
                                entity.AmountOutstanding = 0;
                            }
                            else
                            {
                                entity.CreditNoteStatus = Convert.ToString((Int64)CreditNoteStatus.PartPaid);
                                entity.AmountOutstanding = deposit.isPartAllocated ? deposit.AmountOutstanding - deposit.AmountToAllocate : deposit.AmountToAllocate;
                            }

                            _creditNoteServices.SaveForAllocation(entity);
                        }
                        else if (deposit.ItemType == AllocationItem.SupplierInvoice)
                        {
                            var entity = _supplierInvoiceServices.GetById(deposit.ItemId);
                           
                                if (deposit.isAllocated && deposit.isPartAllocated == false)
                                {
                                    entity.SupplierInvoiceStatus = Convert.ToString((Int64)SupplierInvoiceStatus.Paid);
                                    entity.AmountOutstanding = 0;
                                }
                                else
                                {
                                    entity.SupplierInvoiceStatus = Convert.ToString((Int64)SupplierInvoiceStatus.PartPaid);
                                    entity.AmountOutstanding = deposit.isPartAllocated ? deposit.AmountOutstanding - deposit.AmountToAllocate : deposit.AmountToAllocate;
                            }
                                _supplierInvoiceServices.SaveForAllocation(entity);
                            
                        }
                        else if (deposit.ItemType == AllocationItem.ServiceInvoice)
                        {
                            var serviceInvoice = _servicePurchaseOrderServices.GetById(deposit.ItemId);
                            if (deposit.isAllocated && deposit.isPartAllocated == false)
                            {
                                serviceInvoice.ServiceInvoiceStatus = Convert.ToString((Int64)SupplierInvoiceStatus.Paid);
                                serviceInvoice.AmountOutstanding = 0;
                                serviceInvoice.AmountOutstandingInReportingCurrency = 0;
                            }
                            else
                            {
                                serviceInvoice.ServiceInvoiceStatus = Convert.ToString((Int64)SupplierInvoiceStatus.PartPaid);
                                serviceInvoice.AmountOutstanding = deposit.isPartAllocated ? deposit.AmountOutstanding - deposit.AmountToAllocate : deposit.AmountToAllocate;
                                serviceInvoice.AmountOutstandingInReportingCurrency = getRate(Convert.ToInt64(serviceInvoice.CurrencyID),Convert.ToDecimal(serviceInvoice.AmountOutstanding));
                            }
                            //SaveForAllocation
                            _servicePurchaseOrderServices.SaveForAllocation(serviceInvoice);
                        }
                    }
                }
                #endregion
                #region WithdrawalOutstandingAmount
                if (withdrawalList != null)
                {
                    foreach (var withdrawal in withdrawalList)
                    {
                        if (withdrawal.ItemType == AllocationItem.BankTransactionWithdrawal)
                        {
                            var entity = _bankAccountTransactionServices.GetById(withdrawal.ItemId);
                            if (withdrawal.isAllocated && withdrawal.isPartAllocated == false)
                            {
                                entity.Allocated = Convert.ToString((Int64)BankAccountAllocateType.Allocated);
                                entity.AmountOutstanding = 0;
                            }
                            else
                            {
                                entity.Allocated = Convert.ToString((Int64)BankAccountAllocateType.PartAllocated);
                                entity.AmountOutstanding = withdrawal.isPartAllocated ? withdrawal.AmountOutstanding - withdrawal.AmountToAllocate : withdrawal.AmountToAllocate;
                            }

                            _bankAccountTransactionServices.SaveForAllocation(entity);
                        }
                        else if (withdrawal.ItemType == AllocationItem.CustomerInvoice)
                        {
                            var entity = _invoiceServices.GetById(withdrawal.ItemId);
                            if (withdrawal.isAllocated && withdrawal.isPartAllocated == false)
                            {
                                entity.InvoiceStatus = Convert.ToString((Int64)InvoiceStatus.Paid);
                                entity.AmountOutstanding = 0;
                            }
                            else
                            {
                                entity.InvoiceStatus = Convert.ToString((Int64)InvoiceStatus.PartPaid);
                                entity.AmountOutstanding = withdrawal.isPartAllocated ? withdrawal.AmountOutstanding - withdrawal.AmountToAllocate : withdrawal.AmountToAllocate;
                            }
                            _invoiceServices.SaveForAllocation(entity);
                        }
                        #region AddedbySalman
                        else if (withdrawal.ItemType == AllocationItem.BankTransactionDeposit)
                        {
                            var entity = _bankAccountTransactionServices.GetById(withdrawal.ItemId);//gettting wrong id from view we need backtransaction id
                            if (withdrawal.isAllocated && withdrawal.isPartAllocated == false)
                            {
                                entity.Allocated = Convert.ToString((Int64)BankAccountAllocateType.Allocated);
                                entity.AmountOutstanding = 0;
                            }
                            else
                            {
                                entity.Allocated = Convert.ToString((Int64)BankAccountAllocateType.PartAllocated);
                                entity.AmountOutstanding = withdrawal.isPartAllocated ? withdrawal.AmountOutstanding - withdrawal.AmountToAllocate : withdrawal.AmountToAllocate;
                            }

                            _bankAccountTransactionServices.SaveForAllocation(entity);
                        }
                        #endregion
                        else if (withdrawal.ItemType == AllocationItem.SupplierCreditNote)
                        {
                            var entity = _supplierCreditNoteServices.GetById(withdrawal.ItemId);
                            if (withdrawal.isAllocated && withdrawal.isPartAllocated == false)
                            {
                                entity.CreditNoteStatus = Convert.ToString((Int64)CreditNoteStatus.Paid);
                                entity.AmountOutstanding = 0;
                            }
                            else
                            {
                                entity.CreditNoteStatus = Convert.ToString((Int64)CreditNoteStatus.PartPaid);
                                entity.AmountOutstanding = withdrawal.isPartAllocated ? withdrawal.AmountOutstanding - withdrawal.AmountToAllocate : withdrawal.AmountToAllocate;
                                
                            }
                            _supplierCreditNoteServices.Update(entity);
                        }
                    }
                }
                #endregion
                #endregion

            }
            catch (Exception ex)
            {
                return Json(new { Result = false, Message = "Allocation Failed" });
            }
            return Json(new { Result = true, Message = "Allocated Successfully" });



        }
